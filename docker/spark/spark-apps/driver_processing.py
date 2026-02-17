"""
Same computation as parallel_processing.py but executed entirely on the
driver using Python/pandas — no Spark workers involved.

Run both scripts and compare elapsed times to see the benefit of
distributing work across the cluster.
"""

import time

import numpy as np
import pandas as pd

TOTAL_ROWS = 30_000_000

if __name__ == "__main__":
    print(f"Creating dataset with {TOTAL_ROWS:,} rows on the driver...")
    start_time = time.time()

    df = pd.DataFrame({
        "id": np.arange(TOTAL_ROWS),
        "random_value": np.random.random(TOTAL_ROWS),
    })
    creation_time = time.time() - start_time
    print(f"Dataset created in {creation_time:.2f}s")

    # --- Step 1: heavy per-row math (CPU-bound) ---
    print("\n[Step 1] Per-row math (sin, cos, sqrt, log)...")
    t0 = time.time()
    df["sin_val"] = np.sin(df["random_value"])
    df["cos_val"] = np.cos(df["random_value"])
    df["sqrt_val"] = np.sqrt(df["random_value"])
    df["log_val"] = np.log(df["random_value"] + 1)
    df["composite"] = df["sin_val"] ** 2 + df["cos_val"] ** 2 + df["sqrt_val"]
    step1_time = time.time() - t0
    print(f"  Done in {step1_time:.2f}s")

    # --- Step 2: self-join on partition key ---
    print("\n[Step 2] Self-join (1000 partitions)...")
    t0 = time.time()
    df["partition"] = df["id"] % 1000
    agg_left = df.groupby("partition").agg(
        avg_composite=("composite", "mean"),
        std_random=("random_value", "std"),
        count_id=("id", "count"),
    )
    agg_right = df.groupby("partition").agg(
        min_sin=("sin_val", "min"),
        max_cos=("cos_val", "max"),
        sum_sqrt=("sqrt_val", "sum"),
    )
    joined = agg_left.join(agg_right)
    step2_time = time.time() - t0
    print(f"  Done in {step2_time:.2f}s")

    # --- Step 3: sort full dataset by computed column ---
    print("\n[Step 3] Full sort by composite column...")
    t0 = time.time()
    df_sorted = df.sort_values("composite", ascending=False)
    step3_time = time.time() - t0
    print(f"  Done in {step3_time:.2f}s")

    # --- Step 4: window-like rolling aggregation ---
    print("\n[Step 4] Rolling aggregation (window=1000)...")
    t0 = time.time()
    df_sorted["rolling_avg"] = df_sorted["composite"].rolling(window=1000, min_periods=1).mean()
    step4_time = time.time() - t0
    print(f"  Done in {step4_time:.2f}s")

    total_elapsed = time.time() - start_time

    print(f"\n{'='*50}")
    print(f"DRIVER-ONLY RESULTS ({TOTAL_ROWS:,} rows)")
    print(f"{'='*50}")
    print(f"  Dataset creation : {creation_time:.2f}s")
    print(f"  Step 1 (math)    : {step1_time:.2f}s")
    print(f"  Step 2 (join)    : {step2_time:.2f}s")
    print(f"  Step 3 (sort)    : {step3_time:.2f}s")
    print(f"  Step 4 (rolling) : {step4_time:.2f}s")
    print(f"  TOTAL            : {total_elapsed:.2f}s")
    print(f"\nJoined aggregation sample:")
    print(joined.head(10).to_string())
