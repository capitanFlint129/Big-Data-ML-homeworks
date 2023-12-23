Основной файл
решения: [consumer_with_decorator.py](../consumer_with_decorator.py)

# Подготовка

```bash
docker compose build
docker compose up -d
docker compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --topic itmo2023 --partitions 2 --replication-factor 1
```

Файл device_job.py нужно переместить в flink_dir/

# Backoff

Необходимо запустить flink-джобу, а также продьюсера и консьюмера:

```bash
docker compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job.py -d
bash run_producer_and_consumer_with_decorator.sh
```