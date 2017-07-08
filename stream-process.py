import sys
import logging
import json
import time
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer

logging.basicConfig()
logger = logging.getLogger('stream-process')
logger.setLevel(logging.INFO)

topic = 'stock-analyzer'
broker = 'localhost'
target_topic = 'average-stock-price'
kafka_producer = None

def pair(record):
    """
    :param record: record of stock price
    :return:
    """
    data = json.loads(record[1].decode('utf-8'))[0]
    return data.get('StockSymbol'), (float(data.get('LastTradePrice')), 1)

def send_to_kafka(rdd):
    results = rdd.collect()
    for r in results:
        data = json.dumps(
            {
                'symbol': r[0],
                'timestamp': time.time(),
                'average': r[1]
            }
        )
        print data
        try:
            logger.info('Sending average price %s to kafka' % data)
            kafka_producer.send(target_topic, value=data)
        except KafkaError as error:
            logger.warn('Failed to send average stock price to kafka, caused by: %s', error.message)


def processstream(stream):
    """
    :param stream: input kafka stream
    process thhe input stream
    :return:
    """
    # calculate average
    stream.map(lambda record: pair(record)).reduceByKey(lambda a, b: (a[0]+b[0],a[1]+b[1])).map(lambda (k, v):(k,v[0]/v[1])).foreachRDD(send_to_kafka)

if __name__ == '__main__':
    if len(sys.argv) !=4:
        print ('usgae: stream-process.py kafka-broker kafka-original-topic kafka-new-topic')
        exit(1)

    sc = SparkContext("local[2]", "AverageStackPrice")
    sc.setLogLevel('INFO')
    ssc = StreamingContext(sc, 5)

    broker, topic, target_topic = sys.argv[1:]

    directKafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {'metadata.broker.list':broker})
    processstream(directKafkaStream)

    kafka_producer = KafkaProducer(
        bootstrap_servers = broker
    )

    ssc.start()
    ssc.awaitTermination()