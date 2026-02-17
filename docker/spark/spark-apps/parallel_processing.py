"""
Distributed computation across Spark workers.

Performs the same pipeline as driver_processing.py so elapsed times
are directly comparable.
"""

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    avg, col, cos, count, log, max as _max, min as _min,
    monotonically_increasing_id, rand, sin, sqrt, stddev, sum as _sum,
)
import time

TOTAL_ROWS = 30_000_000

spark = SparkSession.builder \
    .appName("ParallelProcessing") \
    .master("spark://spark-master:7077") \
    .config("spark.executor.instances", "3") \
    .config("spark.executor.cores", "2") \
    .config("spark.executor.memory", "3g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

print(f"Creating dataset with {TOTAL_ROWS:,} rows...")
start_time = time.time()

df = spark.range(0, TOTAL_ROWS).withColumn("random_value", rand())
df = df.repartition(12)
df.cache()
df.count()  # materialise

creation_time = time.time() - start_time
print(f"Dataset created in {creation_time:.2f}s")

# --- Step 1: heavy per-row math (CPU-bound) ---
print("\n[Step 1] Per-row math (sin, cos, sqrt, log)...")
t0 = time.time()
df = df.withColumn("sin_val", sin(col("random_value"))) \
       .withColumn("cos_val", cos(col("random_value"))) \
       .withColumn("sqrt_val", sqrt(col("random_value"))) \
       .withColumn("log_val", log(col("random_value") + 1)) \
       .withColumn("composite", col("sin_val") ** 2 + col("cos_val") ** 2 + col("sqrt_val"))
df.cache()
df.count()  # force evaluation
step1_time = time.time() - t0
print(f"  Done in {step1_time:.2f}s")

# --- Step 2: self-join on partition key ---
print("\n[Step 2] Self-join (1000 partitions)...")
t0 = time.time()
df = df.withColumn("partition", col("id") % 1000)
agg_left = df.groupBy("partition").agg(
    avg("composite").alias("avg_composite"),
    stddev("random_value").alias("std_random"),
    count("id").alias("count_id"),
)
agg_right = df.groupBy("partition").agg(
    _min("sin_val").alias("min_sin"),
    _max("cos_val").alias("max_cos"),
    _sum("sqrt_val").alias("sum_sqrt"),
)
joined = agg_left.join(agg_right, on="partition")
joined.cache()
joined.count()  # force evaluation
step2_time = time.time() - t0
print(f"  Done in {step2_time:.2f}s")

# --- Step 3: sort full dataset by computed column ---
print("\n[Step 3] Full sort by composite column...")
t0 = time.time()
df_sorted = df.orderBy(col("composite").desc())
df_sorted.cache()
df_sorted.count()  # force evaluation
step3_time = time.time() - t0
print(f"  Done in {step3_time:.2f}s")

# --- Step 4: window-based rolling aggregation ---
print("\n[Step 4] Rolling aggregation (window=1000)...")
t0 = time.time()
row_idx = df_sorted.withColumn("row_idx", monotonically_increasing_id())
window_spec = Window.orderBy("row_idx").rowsBetween(-999, 0)
result = row_idx.withColumn("rolling_avg", avg("composite").over(window_spec))
result.cache()
result.count()  # force evaluation
step4_time = time.time() - t0
print(f"  Done in {step4_time:.2f}s")

total_elapsed = time.time() - start_time

print(f"\n{'='*50}")
print(f"DISTRIBUTED RESULTS ({TOTAL_ROWS:,} rows)")
print(f"{'='*50}")
print(f"  Dataset creation : {creation_time:.2f}s")
print(f"  Step 1 (math)    : {step1_time:.2f}s")
print(f"  Step 2 (join)    : {step2_time:.2f}s")
print(f"  Step 3 (sort)    : {step3_time:.2f}s")
print(f"  Step 4 (rolling) : {step4_time:.2f}s")
print(f"  TOTAL            : {total_elapsed:.2f}s")
print(f"\nJoined aggregation sample:")
joined.orderBy("partition").show(10)

spark.stop()
