.PHONY: up up-prod down down-prod status logs spark-shell \
       submit submit-resources submit-py submit-jars dirs pip-install \
       monitoring-up monitoring-down monitoring-status \
       minio-up minio-down jupyter-up jupyter-down download-jars

COMPOSE_FILE       := docker-compose.yaml
COMPOSE_FILE_PROD  := docker-compose.production.yaml
COMPOSE_FILE_MON   := docker-compose.monitoring.yaml
COMPOSE_FILE_MINIO := docker-compose.minio.yaml
COMPOSE_FILE_JUP   := docker-compose.jupyter.yaml
MASTER             := spark-master

# Default app and resource settings (override via CLI: make submit APP=my_job.py)
APP                ?= /opt/spark-apps/my_app.py
EXECUTOR_MEMORY    ?= 4G
EXECUTOR_CORES     ?= 2
TOTAL_CORES        ?= 8
DRIVER_MEMORY      ?= 2G
SHUFFLE_PARTITIONS ?= 100

# --- Cluster lifecycle ---

dirs:
	mkdir -p spark-apps/output spark-data spark-events jars conf
	chmod 777 spark-apps spark-apps/output spark-data spark-events

up: dirs
	docker compose -f $(COMPOSE_FILE) up -d

up-prod: dirs
	docker compose -f $(COMPOSE_FILE_PROD) up -d

down:
	docker compose -f $(COMPOSE_FILE) down

down-prod:
	docker compose -f $(COMPOSE_FILE_PROD) down

status:
	docker compose -f $(COMPOSE_FILE) ps

logs:
	docker compose -f $(COMPOSE_FILE) logs -f

# --- Dependencies ---

PIP_PACKAGES ?= requests pandas pyarrow delta-spark prometheus_client

pip-install:
	@docker compose -f $(COMPOSE_FILE) exec -u 0 -T $(MASTER) pip install --quiet $(PIP_PACKAGES)
	@for worker in $$(docker compose -f $(COMPOSE_FILE) ps --format '{{.Name}}' | grep worker); do \
		docker exec -u 0 $$worker pip install --quiet $(PIP_PACKAGES); \
	done
	@echo "Installed $(PIP_PACKAGES) on all nodes"

# --- Interactive ---

spark-shell:
	docker exec -it $(MASTER) /opt/spark/bin/spark-shell --master spark://$(MASTER):7077

pyspark:
	docker exec -it $(MASTER) /opt/spark/bin/pyspark --master spark://$(MASTER):7077

# --- Spark submit variants ---

submit:
	docker exec -it $(MASTER) /opt/spark/bin/spark-submit \
		--master spark://$(MASTER):7077 \
		--deploy-mode client \
		$(APP)

submit-resources:
	docker exec -it $(MASTER) /opt/spark/bin/spark-submit \
		--master spark://$(MASTER):7077 \
		--deploy-mode client \
		--executor-memory $(EXECUTOR_MEMORY) \
		--executor-cores $(EXECUTOR_CORES) \
		--total-executor-cores $(TOTAL_CORES) \
		--driver-memory $(DRIVER_MEMORY) \
		--conf spark.sql.shuffle.partitions=$(SHUFFLE_PARTITIONS) \
		--conf spark.default.parallelism=$(SHUFFLE_PARTITIONS) \
		$(APP)

submit-py:
	docker exec -it $(MASTER) /opt/spark/bin/spark-submit \
		--master spark://$(MASTER):7077 \
		--py-files $(PY_FILES) \
		$(if $(PACKAGES),--packages $(PACKAGES)) \
		$(APP)

submit-jars:
	docker exec -it $(MASTER) /opt/spark/bin/spark-submit \
		--master spark://$(MASTER):7077 \
		--jars $(JARS) \
		--conf spark.executor.extraJavaOptions="-XX:+UseG1GC" \
		$(APP)

# --- Monitoring ---

monitoring-up:
	docker compose -f $(COMPOSE_FILE_MON) up -d

monitoring-down:
	docker compose -f $(COMPOSE_FILE_MON) down

monitoring-status:
	docker compose -f $(COMPOSE_FILE_MON) ps

# --- MinIO (S3-compatible object storage) ---

minio-up:
	docker compose -f $(COMPOSE_FILE_MINIO) up -d

minio-down:
	docker compose -f $(COMPOSE_FILE_MINIO) down

# --- Jupyter ---

jupyter-up:
	docker compose -f $(COMPOSE_FILE_JUP) up -d

jupyter-down:
	docker compose -f $(COMPOSE_FILE_JUP) down

# --- JARs (Delta Lake + S3A) ---

MAVEN_REPO := https://repo1.maven.org/maven2

download-jars: dirs
	@echo "Downloading Delta Lake and S3A JARs..."
	curl -sL -o jars/delta-spark_2.12-3.0.0.jar $(MAVEN_REPO)/io/delta/delta-spark_2.12/3.0.0/delta-spark_2.12-3.0.0.jar
	curl -sL -o jars/delta-storage-3.0.0.jar $(MAVEN_REPO)/io/delta/delta-storage/3.0.0/delta-storage-3.0.0.jar
	curl -sL -o jars/hadoop-aws-3.3.4.jar $(MAVEN_REPO)/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar
	curl -sL -o jars/aws-java-sdk-bundle-1.12.262.jar $(MAVEN_REPO)/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar
	@echo "Done. JARs saved to jars/"
