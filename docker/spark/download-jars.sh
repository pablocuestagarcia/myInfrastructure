#!/usr/bin/env bash
#
# Downloads the JARs required for Delta Lake and S3A (MinIO) support
# on Apache Spark 3.5.0.
#
# Usage: ./download-jars.sh
#
set -euo pipefail

JARS_DIR="$(cd "$(dirname "$0")" && pwd)/jars"
MAVEN="https://repo1.maven.org/maven2"

declare -A JARS=(
  ["delta-spark_2.12-3.0.0.jar"]="io/delta/delta-spark_2.12/3.0.0"
  ["delta-storage-3.0.0.jar"]="io/delta/delta-storage/3.0.0"
  ["hadoop-aws-3.3.4.jar"]="org/apache/hadoop/hadoop-aws/3.3.4"
  ["aws-java-sdk-bundle-1.12.262.jar"]="com/amazonaws/aws-java-sdk-bundle/1.12.262"
)

mkdir -p "$JARS_DIR"

for jar in "${!JARS[@]}"; do
  path="${JARS[$jar]}"
  dest="$JARS_DIR/$jar"

  if [[ -f "$dest" ]]; then
    echo "SKIP  $jar (already exists)"
    continue
  fi

  echo "GET   $jar"
  curl -sL -o "$dest" "$MAVEN/$path/$jar"
  echo "OK    $jar ($(du -h "$dest" | cut -f1))"
done

echo ""
echo "All JARs ready in $JARS_DIR"
ls -lh "$JARS_DIR"
