from kafka.client import SimpleClient
from kafka.producer import KafkaProducer
import twitter
from time import sleep
from datetime import datetime

kafka = SimpleClient("localhost:9092")
producer = KafkaProducer(bootstrap_servers='localhost:9092')


api = twitter.Api(consumer_key='***REMOVED***',
                  consumer_secret='***REMOVED***',
                  access_token_key='***REMOVED***',
                  access_token_secret='***REMOVED***')

for status in api.GetStreamFilter(track=['trump']):
	
	if 'text' in status:
		text = status['text']
		print text
		producer.send("kafkaesque",text.encode('utf-8'))	
