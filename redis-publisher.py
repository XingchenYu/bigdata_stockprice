# read from any kafka broker and topic
# relay to redis channel
from kafka import KafkaConsumer

import argparse
import redis
import logging
import atexit

logging.basicConfig()
logger = logging.getLogger('redis-publisher')
logger.setLevel(logging.DEBUG)

def shutdown_hook(kafka_consumer):
    logger.info('closing kafka client')
    kafka_consumer.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('topic_name', help='the kafka topic')
    parser.add_argument('kafka_broker', help='the location of kafka')
    parser.add_argument('redis_host', help='the ip of the redis server')
    parser.add_argument('redis_port', help='the port of the redis server')
    parser.add_argument('redis_channel', help='the channel to publish to')

    args = parser.parse_args()
    topic_name = args.topic_name
    kafka_broker = args.kafka_broker
    redis_host = args.redis_host
    redis_port = args.redis_port
    redis_channel = args.redis_channel

    kafka_consumer = KafkaConsumer(topic_name, bootstrap_servers=kafka_broker)

    redis_client = redis.StrictRedis(host=redis_host, port=redis_port)

    atexit.register(shutdown_hook, kafka_consumer)

    for msg in kafka_consumer:
        logger.info('received data from kafka {0} and sent to redis_channel {1}'.format(str(msg), redis_channel) )
        redis_client.publish(redis_channel, msg.value)