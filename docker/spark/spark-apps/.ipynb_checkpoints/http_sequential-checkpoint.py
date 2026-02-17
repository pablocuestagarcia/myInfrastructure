"""
HTTP requests executed sequentially in a single process (the driver).
Results are loaded into a Spark DataFrame and saved as JSON.
"""

from pyspark.sql import SparkSession
import requests
import time


API_URL = "https://jsonplaceholder.typicode.com/posts/{}"
TOTAL_REQUESTS = 100
OUTPUT_PATH = "/opt/spark-apps/output/sequential"


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("HTTPSequential") \
        .master("spark://spark-master:7077") \
        .config("spark.eventLog.enabled", "true") \
        .config("spark.eventLog.dir", "/opt/spark/spark-events") \
        .getOrCreate()

    print(f"\n=== SEQUENTIAL: fetching {TOTAL_REQUESTS} posts from driver ===\n")
    start = time.time()

    results = []
    for i in range(1, TOTAL_REQUESTS + 1):
        response = requests.get(API_URL.format(i))
        data = response.json()
        results.append((data["id"], data["userId"], data["title"], len(data["title"])))

    fetch_elapsed = time.time() - start
    print(f"Fetch completed in {fetch_elapsed:.2f}s")

    df = spark.createDataFrame(results, ["id", "user_id", "title", "title_length"])

    df.write.mode("overwrite").json(OUTPUT_PATH)

    total_elapsed = time.time() - start
    print(f"\nTotal: {total_elapsed:.2f}s (fetch: {fetch_elapsed:.2f}s, spark write: {total_elapsed - fetch_elapsed:.2f}s)")
    print(f"Avg per request: {fetch_elapsed / TOTAL_REQUESTS * 1000:.0f}ms")
    df.show(5, truncate=60)

    spark.stop()
