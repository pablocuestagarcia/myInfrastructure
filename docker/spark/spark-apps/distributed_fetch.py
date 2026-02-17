"""
General-purpose distributed HTTP fetcher for PySpark.

Two factory functions are provided:
- create_fetcher:            For on-prem / Docker environments. Supports optional
                             Prometheus Pushgateway instrumentation.
- create_databricks_fetcher: For Databricks. No Prometheus dependency.
                             Logs appear in Spark UI > Executors > stderr.

Both return functions compatible with DataFrame.mapInPandas() and produce
DataFrames matching RESPONSE_SCHEMA.

Usage (on-prem):
    from distributed_fetch import create_fetcher, RESPONSE_SCHEMA

    results_df = urls_df.repartition(4).mapInPandas(
        create_fetcher(pushgateway_url="http://pushgateway:9091"),
        schema=RESPONSE_SCHEMA,
    )

Usage (Databricks):
    from distributed_fetch import create_databricks_fetcher, RESPONSE_SCHEMA

    results_df = urls_df.repartition(4).mapInPandas(
        create_databricks_fetcher(timeout=5),
        schema=RESPONSE_SCHEMA,
    )
"""

from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType,
)

RESPONSE_SCHEMA = StructType([
    StructField("url", StringType()),
    StructField("status_code", IntegerType()),
    StructField("body", StringType()),
    StructField("content_type", StringType()),
    StructField("elapsed_ms", DoubleType()),
    StructField("worker", StringType()),
    StructField("error", StringType()),
])


# ---------------------------------------------------------------------------
# On-prem / Docker  (optional Prometheus Pushgateway)
# ---------------------------------------------------------------------------

def create_fetcher(
    url_column="url",
    method="GET",
    headers=None,
    body_column=None,
    timeout=10,
    max_retries=0,
    pushgateway_url=None,
    job_name="distributed_fetch",
):
    """
    Factory that returns a function compatible with DataFrame.mapInPandas().

    The returned function reads URLs from *url_column*, performs HTTP requests
    on the workers, and yields DataFrames matching RESPONSE_SCHEMA.

    Args:
        url_column:      Column containing the target URLs.
        method:          HTTP method (GET, POST, PUT, DELETE, PATCH).
        headers:         Dict of headers added to every request.
        body_column:     Column containing the request body (POST/PUT/PATCH).
        timeout:         Per-request timeout in seconds.
        max_retries:     Retries on transient errors (5xx, connection reset).
                         0 means no retries beyond the initial attempt.
        pushgateway_url: If set, pushes per-worker metrics to this Pushgateway.
        job_name:        Job label for Pushgateway grouping.

    Returns:
        A callable for DataFrame.mapInPandas(fn, schema=RESPONSE_SCHEMA).
    """
    _method = method.upper()
    _headers = dict(headers) if headers else {}
    _url_col = url_column
    _body_col = body_column
    _timeout = timeout
    _max_retries = max_retries
    _pg_url = pushgateway_url
    _job = job_name

    def _fetch(partitions_iter):
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import logging
        import socket
        import time
        import pandas as pd

        log = logging.getLogger("distributed_fetch")
        hostname = socket.gethostname()

        # --- optional Prometheus instrumentation ---
        registry = counter = histogram = None
        if _pg_url:
            from prometheus_client import CollectorRegistry, Counter, Histogram
            registry = CollectorRegistry()
            counter = Counter(
                "spark_http_requests_total", "HTTP requests",
                ["worker", "status"], registry=registry,
            )
            histogram = Histogram(
                "spark_http_request_duration_seconds", "HTTP latency",
                ["worker"], registry=registry,
            )

        # --- session with connection pooling and optional retries ---
        session = requests.Session()
        if _headers:
            session.headers.update(_headers)
        if _max_retries > 0:
            strategy = Retry(
                total=_max_retries,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504],
            )
            session.mount("http://", HTTPAdapter(max_retries=strategy))
            session.mount("https://", HTTPAdapter(max_retries=strategy))

        log.info("[%s] Session created | method=%s timeout=%s retries=%s",
                 hostname, _method, _timeout, _max_retries)

        with session:
            for partition_df in partitions_iter:
                total = len(partition_df)
                ok_count = 0
                err_count = 0
                results = []

                log.info("[%s] Partition received | %d URLs to fetch", hostname, total)

                for _, row in partition_df.iterrows():
                    url = row[_url_col]
                    body = (
                        row[_body_col]
                        if _body_col and _body_col in row.index
                        else None
                    )

                    start = time.time()
                    try:
                        resp = session.request(
                            _method, url, data=body, timeout=_timeout,
                        )
                        elapsed_ms = (time.time() - start) * 1000

                        if histogram:
                            histogram.labels(worker=hostname).observe(elapsed_ms / 1000)

                        if resp.ok:
                            if counter:
                                counter.labels(worker=hostname, status="success").inc()
                            error = None
                            ok_count += 1
                            log.debug("[%s] %s %s -> %d (%.0fms)",
                                      hostname, _method, url, resp.status_code, elapsed_ms)
                        else:
                            if counter:
                                counter.labels(worker=hostname, status="error").inc()
                            error = f"HTTP {resp.status_code}"
                            err_count += 1
                            log.warning("[%s] %s %s -> %d (%.0fms)",
                                        hostname, _method, url, resp.status_code, elapsed_ms)

                        results.append({
                            "url": url,
                            "status_code": resp.status_code,
                            "body": resp.text,
                            "content_type": resp.headers.get("Content-Type"),
                            "elapsed_ms": elapsed_ms,
                            "worker": hostname,
                            "error": error,
                        })

                    except requests.RequestException as exc:
                        elapsed_ms = (time.time() - start) * 1000
                        err_count += 1
                        if counter:
                            counter.labels(worker=hostname, status="error").inc()
                        log.error("[%s] %s %s -> FAILED after %.0fms: %s",
                                  hostname, _method, url, elapsed_ms, exc)
                        results.append({
                            "url": url,
                            "status_code": None,
                            "body": None,
                            "content_type": None,
                            "elapsed_ms": elapsed_ms,
                            "worker": hostname,
                            "error": str(exc),
                        })

                log.info("[%s] Partition done | %d/%d succeeded, %d failed",
                         hostname, ok_count, total, err_count)
                yield pd.DataFrame(results)

        # --- push metrics after all partitions are processed ---
        if registry and _pg_url:
            from prometheus_client import push_to_gateway
            try:
                push_to_gateway(
                    _pg_url, job=_job,
                    grouping_key={"worker": hostname},
                    registry=registry,
                )
                log.info("[%s] Metrics pushed to %s", hostname, _pg_url)
            except Exception as exc:
                log.warning("[%s] Failed to push metrics: %s", hostname, exc)

    return _fetch


# ---------------------------------------------------------------------------
# Databricks  (no Prometheus, logging goes to executor stderr)
# ---------------------------------------------------------------------------

def create_databricks_fetcher(
    url_column="url",
    method="GET",
    headers=None,
    body_column=None,
    timeout=10,
    max_retries=0,
):
    """
    Factory for Databricks: returns a mapInPandas-compatible HTTP fetcher.

    Same interface as create_fetcher but without Prometheus dependencies.
    Logs are written via Python logging and appear in:
      - Driver logs   -> notebook cell output / driver log4j
      - Worker logs   -> Spark UI > Executors > stderr

    Args:
        url_column:  Column containing the target URLs.
        method:      HTTP method (GET, POST, PUT, DELETE, PATCH).
        headers:     Dict of headers added to every request.
        body_column: Column containing the request body (POST/PUT/PATCH).
        timeout:     Per-request timeout in seconds.
        max_retries: Retries on transient errors (5xx, connection reset).
                     0 means no retries beyond the initial attempt.

    Returns:
        A callable for DataFrame.mapInPandas(fn, schema=RESPONSE_SCHEMA).
    """
    _method = method.upper()
    _headers = dict(headers) if headers else {}
    _url_col = url_column
    _body_col = body_column
    _timeout = timeout
    _max_retries = max_retries

    def _fetch(partitions_iter):
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import logging
        import socket
        import time
        import pandas as pd

        log = logging.getLogger("distributed_fetch.databricks")
        if not log.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%H:%M:%S",
            ))
            log.addHandler(handler)
            log.setLevel(logging.INFO)

        hostname = socket.gethostname()

        session = requests.Session()
        if _headers:
            session.headers.update(_headers)
        if _max_retries > 0:
            strategy = Retry(
                total=_max_retries,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504],
            )
            session.mount("http://", HTTPAdapter(max_retries=strategy))
            session.mount("https://", HTTPAdapter(max_retries=strategy))

        log.info("[%s] Session created | method=%s timeout=%s retries=%s",
                 hostname, _method, _timeout, _max_retries)

        with session:
            for partition_df in partitions_iter:
                total = len(partition_df)
                ok_count = 0
                err_count = 0
                results = []

                log.info("[%s] Partition received | %d URLs to fetch", hostname, total)

                for _, row in partition_df.iterrows():
                    url = row[_url_col]
                    body = (
                        row[_body_col]
                        if _body_col and _body_col in row.index
                        else None
                    )

                    start = time.time()
                    try:
                        resp = session.request(
                            _method, url, data=body, timeout=_timeout,
                        )
                        elapsed_ms = (time.time() - start) * 1000

                        if resp.ok:
                            error = None
                            ok_count += 1
                            log.debug("[%s] %s %s -> %d (%.0fms)",
                                      hostname, _method, url, resp.status_code, elapsed_ms)
                        else:
                            error = f"HTTP {resp.status_code}"
                            err_count += 1
                            log.warning("[%s] %s %s -> %d (%.0fms)",
                                        hostname, _method, url, resp.status_code, elapsed_ms)

                        results.append({
                            "url": url,
                            "status_code": resp.status_code,
                            "body": resp.text,
                            "content_type": resp.headers.get("Content-Type"),
                            "elapsed_ms": elapsed_ms,
                            "worker": hostname,
                            "error": error,
                        })

                    except requests.RequestException as exc:
                        elapsed_ms = (time.time() - start) * 1000
                        err_count += 1
                        log.error("[%s] %s %s -> FAILED after %.0fms: %s",
                                  hostname, _method, url, elapsed_ms, exc)
                        results.append({
                            "url": url,
                            "status_code": None,
                            "body": None,
                            "content_type": None,
                            "elapsed_ms": elapsed_ms,
                            "worker": hostname,
                            "error": str(exc),
                        })

                log.info("[%s] Partition done | %d/%d succeeded, %d failed",
                         hostname, ok_count, total, err_count)
                yield pd.DataFrame(results)

    return _fetch
