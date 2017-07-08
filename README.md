# bigdata_stockprice
Interactive with Kafka and Zookeeper servers, catch stock price from google finance and write to Kafka, and interactive with Cassandra servers and save data to Cassandra based on Cassandra driver. Finally show real-time stock price.

Some steps:

use redis to publish and subscribe:
./redis-cli -h localhost

start server:
docker run -d -p 2181:2181 -p 2888:2888 -p 3888:3888 --name zookeeper confluent/zookeeper
docker run -d -p 9092:9092 -e KAFKA_ADVERTISED_HOST_NAME=localhost -e KAFKA_ADVERTISED_PORT=9092 --name kafka --link zookeeper:zookeeper confluent/kafka
docker run -d -p 6379:6379 --name redis redis:alpine

ENV_CONFIG_FILE="path/to/config/dev.cfg"

1.Kafka producer:
python flask-data-producer.py
use postman to post {result:[AAPL]} to localhost:5000/AAPL

2.Comsumer(Spark):
./spark-submit --jars spark-streaming-kafka-0-8-assembly_2.11-2.0.0.jar stream-process.py stock-analyzer average-stock-price localhost:9092

3.Redis publisher:
python redis-publisher.py average-stock-price localhost localhost 6379 stock-price

4.Node.js:
node index.js --port=3000 --redis_host=localhost --redis_port=6379 --subscribe_topic=stock-price