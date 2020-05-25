from kafka import KafkaProducer
from kafka import KafkaClient

import twitter
from time import sleep
from datetime import datetime


def get_producer():
	is_connected=False
	producer = None
	while not is_connected:
		
		try:
			sleep(1)
			producer = KafkaProducer(bootstrap_servers='localhost:9093')
			is_connected=True

		except Exception:
			print('error connecting')
			pass
	
	return producer

api = twitter.Api(consumer_key='YnJhmBnBkaRY9KrIRoidA',
                  consumer_secret='lAdMxNrYqKxWJ8mh8g79AYiUGIxnCqG2V3soOZnnwVM',
                  access_token_key='556210107-2gQxW6J54wErB9t0YlqqfH6IZPCRgQa6rkTlMCc3',
                  access_token_secret='ikjvynp1eZRoxRsdPtQPS4DpCigKxpHEN27RAFPU')

producer = get_producer()
for status in api.GetStreamFilter(track=['covid']):
	if 'text' in status:
		text = status['text']
		producer.send("twitter",key='covid',value=text.encode('utf-8'))	
