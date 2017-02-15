from kafka.client import SimpleClient
from kafka.producer import KafkaProducer
from time import sleep
from datetime import datetime

kafka = SimpleClient("localhost:9092")
producer = KafkaProducer(bootstrap_servers='localhost:9092')

while 1:
  # "kafkaesque" is the name of our topic
  producer.send("kafkaesque",b'Metamorphosis!')
  sleep(1)
