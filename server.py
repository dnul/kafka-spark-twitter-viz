from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room
from kafka.client import SimpleClient
from kafka.producer import KafkaProducer
from time import sleep
from datetime import datetime
from flask import jsonify
from flask import make_response
from concurrent.futures import ThreadPoolExecutor
import twitter
import json


class TwitterSearchProducer():
    def __init__(self):
        self.kafka = SimpleClient("localhost:9092")
        self.api = twitter.Api(consumer_key='YnJhmBnBkaRY9KrIRoidA',
            consumer_secret='lAdMxNrYqKxWJ8mh8g79AYiUGIxnCqG2V3soOZnnwVM',
            access_token_key='556210107-2gQxW6J54wErB9t0YlqqfH6IZPCRgQa6rkTlMCc3',
            access_token_secret='ikjvynp1eZRoxRsdPtQPS4DpCigKxpHEN27RAFPU')
        self.producer = KafkaProducer(bootstrap_servers='localhost:9092')

    def search(self,term):
		for status in self.api.GetStreamFilter(track=['trump']):
			if 'text' in status:
				text = status['text']
				self.producer.send("kafkaesque",text.encode('utf-8'))

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
socketio = SocketIO(app)
searchApi = TwitterSearchProducer()


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/search',methods=['POST'])
def search():
    executor.submit(searchApi.search,'trump')
    return ('',200)


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('customevent')
def handle_custom_event(jsonData):
	print('received custom event' + str(jsonData))
	socketio.emit('update',json.dumps(jsonData,ensure_ascii=False),room='feed')

@socketio.on('subscribe')
def handle_suscribe():
	join_room('feed')






if __name__ == '__main__':
#	app.run(debug=True)
	socketio.run(app,debug=True)
