Основной файл решения: [device_job_windows.py](../device_job_windows.py)

Для запуска файла с разными типами окон нужно раскомментировать
соответствующие строчки (78, 79 или 80).

# Подготовка

```bash
docker compose build
docker compose up -d
docker compose exec kafka kafka-topics.sh --bootstrap-server kafka:9092 --create --topic itmo2023 --partitions 2 --replication-factor 1
```

Файл device_job_windows.py нужно переместить в flink_dir/

# Windows

Необходимо запустить flink-джобу, а также продьюсера и консьюмера:

```bash
docker compose exec jobmanager ./bin/flink run -py /opt/pyflink/device_job_windows.py -d
bash run_producer_and_consumer.sh
```