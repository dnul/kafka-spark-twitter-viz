# -*- coding: UTF-8 -*-

import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from kafka import KafkaProducer
from kafka import KafkaClient
from pyspark import SparkConf
import socketio.client
import os
from time import sleep

KAFKA_BROKER = os.environ.get('kafka_broker')
SERVER_WEBSOCKET = os.environ.get('server_ws')

def wait_for_kafka():
	is_connected=False
	producer = None
	while not is_connected:
		
		try:
			sleep(10)
			producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
			is_connected=True

		except Exception:
			print('error connecting')
			pass
	
	return producer



if __name__ == "__main__":
    conf = SparkConf().set("spark.jars", "./spark-streaming-kafka-0-8-assembly_2.11-2.4.5.jar")
    #conf = SparkConf().set("spark.jars", "spark-streaming-kafka-0-8_2.11-2.4.5.jar")
    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount",conf=conf)
    ssc = StreamingContext(sc, 2)
    ssc.checkpoint("checkpoint")

    #common words
    common_words_file = open('common_tweet_words.txt')
    common_words = {}
    for line in common_words_file.readlines():
        common_words[line.strip('\n')] = True



    # RDD with initial state (key, value) pairs
    initialStateRDD = sc.parallelize([(u'hello', 1), (u'world', 1)])

    def getConnection():
        ws = socketio.Client()
        ws.connect('http://'+SERVER_WEBSOCKET)
        return ws

    def sendRDDPartition(rdd):
        ws = getConnection()
        values = rdd.take(10)
        print(values)
        ws.emit('spark-update',values)
        ws.disconnect()


    def updateFunc(new_values, last_sum):
        return sum(new_values) + (last_sum or 0)

    wait_for_kafka()

    kvs = KafkaUtils.createDirectStream(ssc, ["kafkaesque"], {"bootstrap.servers": KAFKA_BROKER})
    lines = kvs.map(lambda x: x[1])


    running_counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word.lower(), 1)) \
        .filter(lambda x: x[0].lower() not in common_words and len(x[0])>3)\
        .reduceByKeyAndWindow(lambda x,y:x+y,24,4,slideDuration=2)
        

    sorted_counts =  running_counts.transform(lambda rdd: rdd.sortBy(lambda x: -x[1]))

    sorted_counts.pprint()

    result = sorted_counts.foreachRDD(sendRDDPartition)


    ssc.start()
    ssc.awaitTermination()