"""
HTTP requests executed in parallel across Spark workers using mapInPandas.

Best practices applied:
- mapInPandas instead of rdd.mapPartitions (Arrow serialization, stays in DataFrame API)
- requests.Session for connection pooling within each partition
- Explicit error handling per request to avoid losing an entire partition on failure
- Prometheus Pushgateway instrumentation for per-worker HTTP metrics
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import time


API_URL = "https://jsonplaceholder.typicode.com/posts/{}"
TOTAL_REQUESTS = 100
NUM_PARTITIONS = 2
OUTPUT_PATH = "/opt/spark-apps/output/distributed_bp"
PUSHGATEWAY_URL = "http://spark-pushgateway:9091"


def fetch_posts(partitions_iter):
    """Runs on each worker. Receives an iterator of pandas DataFrames (one per batch)."""
    import requests
    import socket
    import pandas as pd
    from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway

    hostname = socket.gethostname()

    registry = CollectorRegistry()
    http_requests_total = Counter(
        "spark_http_requests_total",
        "Total HTTP requests made by this worker",
        ["worker", "status"],
        registry=registry,
    )
    http_request_duration = Histogram(
        "spark_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["worker"],
        registry=registry,
    )

    with requests.Session() as session:
        for partition_df in partitions_iter:
            results = []
            for post_id in partition_df["id"]:
                try:
                    req_start = time.time()
                    response = session.get(API_URL.format(post_id), timeout=10)
                    response.raise_for_status()
                    http_request_duration.labels(worker=hostname).observe(time.time() - req_start)
                    http_requests_total.labels(worker=hostname, status="success").inc()
                    data = response.json()
                    results.append((
                        int(data["id"]),
                        int(data["userId"]),
                        data["title"],
                        len(data["title"]),
                        hostname,
                    ))
                except requests.RequestException:
                    http_requests_total.labels(worker=hostname, status="error").inc()
                    results.append((int(post_id), None, None, None, hostname))

            yield pd.DataFrame(results, columns=["id", "user_id", "title", "title_length", "worker"])

    try:
        push_to_gateway(PUSHGATEWAY_URL, job="http_distributed_bp", grouping_key={"worker": hostname}, registry=registry)
    except Exception:
        pass


schema = StructType([
    StructField("id", IntegerType()),
    StructField("user_id", IntegerType()),
    StructField("title", StringType()),
    StructField("title_length", IntegerType()),
    StructField("worker", StringType()),
])


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("HTTPDistributedBP") \
        .master("spark://spark-master:7077") \
        .config("spark.eventLog.enabled", "true") \
        .config("spark.eventLog.dir", "/opt/spark/spark-events") \
        .getOrCreate()

    print(f"\n=== DISTRIBUTED (BP): fetching {TOTAL_REQUESTS} posts across {NUM_PARTITIONS} partitions ===\n")
    start = time.time()

    ids_df = spark.createDataFrame(
        [(i,) for i in range(1, TOTAL_REQUESTS + 1)],
        ["id"],
    ).repartition(NUM_PARTITIONS)

    results_df = ids_df.mapInPandas(fetch_posts, schema=schema)

    results_df.write.mode("overwrite").json(OUTPUT_PATH)

    total_elapsed = time.time() - start
    print(f"\nTotal: {total_elapsed:.2f}s")
    print(f"Avg per request: {total_elapsed / TOTAL_REQUESTS * 1000:.0f}ms")
    print(f"Partitions used: {NUM_PARTITIONS}")

    results_df = spark.read.json(OUTPUT_PATH)
    results_df.show(5, truncate=60)

    spark.stop()
