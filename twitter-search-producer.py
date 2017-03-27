from kafka.client import SimpleClient
from kafka.producer import KafkaProducer
import twitter
from time import sleep
from datetime import datetime

kafka = SimpleClient("localhost:9092")
producer = KafkaProducer(bootstrap_servers='localhost:9092')


api = twitter.Api(consumer_key='YnJhmBnBkaRY9KrIRoidA',
                  consumer_secret='lAdMxNrYqKxWJ8mh8g79AYiUGIxnCqG2V3soOZnnwVM',
                  access_token_key='556210107-2gQxW6J54wErB9t0YlqqfH6IZPCRgQa6rkTlMCc3',
                  access_token_secret='ikjvynp1eZRoxRsdPtQPS4DpCigKxpHEN27RAFPU')

for status in api.GetStreamFilter(track=['trump']):
	
	if 'text' in status:
		text = status['text']
		print text
		producer.send("kafkaesque",text.encode('utf-8'))	
