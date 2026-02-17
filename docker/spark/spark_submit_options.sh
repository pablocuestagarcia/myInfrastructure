# Configuring Resources
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --executor-memory 4G \
  --executor-cores 2 \
  --total-executor-cores 8 \
  --driver-memory 2G \
  --conf spark.sql.shuffle.partitions=100 \
  --conf spark.default.parallelism=100 \
  /opt/spark-apps/my_app.py

  # Another parallel submit
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --executor-memory 2G \
  --total-executor-cores 6 \
  /opt/spark-apps/parallel_processing.py


# With Python Dependencies
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --py-files /opt/spark-apps/dependencies.zip \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /opt/spark-apps/streaming_app.py

# With External JARs
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --jars /opt/spark/jars/postgresql-42.7.1.jar,/opt/spark/jars/mysql-connector-java-8.0.30.jar \
  --conf spark.executor.extraJavaOptions="-XX:+UseG1GC" \
  /opt/spark-apps/etl_job.py
