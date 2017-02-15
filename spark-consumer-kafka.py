# -*- coding: UTF-8 -*-

import sys

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from socketIO_client import SocketIO, LoggingNamespace


if __name__ == "__main__":
    #if len(sys.argv) != 3:
    #    print("Usage: direct_kafka_wordcount.py <broker_list> <topic>", file=sys.stderr)
    #    exit(-1)

    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
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
        ws = SocketIO('localhost',5000)
        return ws

    def sendRDDPartition(rdd):
        ws = getConnection()
        values = rdd.take(10)
        ws.emit('customevent',values)
        


    def updateFunc(new_values, last_sum):
        return sum(new_values) + (last_sum or 0)

    kvs = KafkaUtils.createDirectStream(ssc, ["kafkaesque"], {"bootstrap.servers": 'localhost:9092'})
    lines = kvs.map(lambda x: x[1])


    running_counts = lines.flatMap(lambda line: line.split(" ")) \
        .map(lambda word: (word, 1)) \
        .filter(lambda x: x[0].lower() not in common_words and len(x[0])>3)\
        .reduceByKeyAndWindow(lambda x,y:x+y,24,4,slideDuration=2)
        

    sorted_counts =  running_counts.transform(lambda rdd: rdd.sortBy(lambda x: -x[1]))

    
    sorted_counts.pprint()

    result = sorted_counts.foreachRDD(sendRDDPartition)


    ssc.start()
    ssc.awaitTermination()