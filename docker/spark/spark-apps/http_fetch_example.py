"""
Example usage of the distributed_fetch module.

Fetches data from the PokeAPI (https://pokeapi.co) across Spark workers
using create_fetcher with Prometheus Pushgateway instrumentation.

Usage:
    make submit APP=/opt/spark-apps/http_fetch_example.py

    # or with more partitions:
    make submit APP=/opt/spark-apps/http_fetch_example.py
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, get_json_object
import time

from distributed_fetch import create_fetcher, RESPONSE_SCHEMA

TOTAL_POKEMON = 80
NUM_PARTITIONS = 4
OUTPUT_PATH = "/opt/spark-apps/output/fetch_example"
PUSHGATEWAY_URL = "http://spark-pushgateway:9091"

if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("HTTPFetchExample") \
        .master("spark://spark-master:7077") \
        .config("spark.eventLog.enabled", "true") \
        .config("spark.eventLog.dir", "/opt/spark/spark-events") \
        .getOrCreate()

    # --- Build a DataFrame of URLs to fetch ---
    urls_df = spark.createDataFrame(
        [(f"https://pokeapi.co/api/v2/pokemon/{i}",) for i in range(1, TOTAL_POKEMON + 1)],
        ["url"],
    ).repartition(NUM_PARTITIONS)

    print(f"\n=== Fetching {TOTAL_POKEMON} Pokemon across {NUM_PARTITIONS} partitions ===\n")
    print("Sample URLs:")
    print(urls_df.show(5, truncate=False))
    start = time.time()

    # --- Distributed fetch using the reusable module ---
    fetcher = create_fetcher(
        timeout=10,
        max_retries=2,
        pushgateway_url=PUSHGATEWAY_URL,
        job_name="pokemon_fetch",
    )
    results_df = urls_df.mapInPandas(fetcher, schema=RESPONSE_SCHEMA)

    # --- Extract fields from the JSON body ---
    pokemon_df = results_df.filter(col("error").isNull()).select(
        col("url"),
        col("worker"),
        col("elapsed_ms"),
        get_json_object(col("body"), "$.name").alias("name"),
        get_json_object(col("body"), "$.id").cast("int").alias("pokedex_id"),
        get_json_object(col("body"), "$.height").cast("int").alias("height"),
        get_json_object(col("body"), "$.weight").cast("int").alias("weight"),
        get_json_object(col("body"), "$.base_experience").cast("int").alias("base_xp"),
    )

    pokemon_df.cache()
    total_count = pokemon_df.count()
    fetch_elapsed = time.time() - start

    # --- Show results ---
    print(f"\nFetched {total_count}/{TOTAL_POKEMON} Pokemon in {fetch_elapsed:.2f}s")
    print(f"Avg per request: {fetch_elapsed / TOTAL_POKEMON * 1000:.0f}ms\n")

    print("Sample results:")
    pokemon_df.orderBy("pokedex_id").show(10, truncate=False)

    print("Requests per worker:")
    pokemon_df.groupBy("worker").count().show()

    # --- Save to JSON ---
    pokemon_df.write.mode("overwrite").json(OUTPUT_PATH)
    print(f"Results saved to {OUTPUT_PATH}")

    # --- Check errors ---
    errors_df = results_df.filter(col("error").isNotNull())
    error_count = errors_df.count()
    if error_count > 0:
        print(f"\n{error_count} requests failed:")
        errors_df.select("url", "error", "worker").show(truncate=False)

    spark.stop()
