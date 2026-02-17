"""
HTTP requests executed in parallel across Spark workers.
Each partition runs its batch of calls independently on different executors.
Results are saved as JSON.
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
import time


API_URL = "https://jsonplaceholder.typicode.com/posts/{}"
TOTAL_REQUESTS = 100
NUM_PARTITIONS = 2
OUTPUT_PATH = "/opt/spark-apps/output/distributed"


def fetch_posts(partition):
    """Runs on each worker — imports happen at the executor, not the driver."""
    import requests
    import socket

    hostname = socket.gethostname()

    for row in partition:
        post_id = row["id"]
        response = requests.get(API_URL.format(post_id))
        data = response.json()
        yield (data["id"], data["userId"], data["title"], len(data["title"]), hostname)


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("HTTPDistributed") \
        .master("spark://spark-master:7077") \
        .config("spark.eventLog.enabled", "true") \
        .config("spark.eventLog.dir", "/opt/spark/spark-events") \
        .getOrCreate()

    print(f"\n=== DISTRIBUTED: fetching {TOTAL_REQUESTS} posts across {NUM_PARTITIONS} partitions ===\n")
    start = time.time()

    ids_df = spark.createDataFrame(
        [(i,) for i in range(1, TOTAL_REQUESTS + 1)],
        ["id"],
    ).repartition(NUM_PARTITIONS)

    schema = StructType([
        StructField("id", IntegerType()),
        StructField("user_id", IntegerType()),
        StructField("title", StringType()),
        StructField("title_length", IntegerType()),
        StructField("worker", StringType()),
    ])

    results_df = spark.createDataFrame(
        ids_df.rdd.mapPartitions(fetch_posts),
        schema,
    )

    results_df.write.mode("overwrite").json(OUTPUT_PATH)

    total_elapsed = time.time() - start
    print(f"\nTotal: {total_elapsed:.2f}s")
    print(f"Avg per request: {total_elapsed / TOTAL_REQUESTS * 1000:.0f}ms")
    print(f"Partitions used: {NUM_PARTITIONS}")

    results_df = spark.read.json(OUTPUT_PATH)
    results_df.show(5, truncate=60)

    spark.stop()
