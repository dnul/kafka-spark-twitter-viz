from flask import Flask, request, session
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room
from kafka import KafkaConsumer, KafkaProducer
from time import sleep
from datetime import datetime
from flask import jsonify
from flask import make_response
from concurrent.futures import ThreadPoolExecutor
import twitter
import json
import os


KAFKA_BROKER = os.environ.get("kafka_broker")
TWITTER_CONSUMER_KEY= os.environ.get("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET= os.environ.get("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN_KEY= os.environ.get("TWITTER_ACCESS_TOKEN_KEY")
TWITTER_ACCESS_TOKEN_SECRET= os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                  consumer_secret=TWITTER_CONSUMER_SECRET,
                  access_token_key=TWITTER_ACCESS_TOKEN_KEY,
                  access_token_secret=TWITTER_ACCESS_TOKEN_SECRET)


def get_producer():
	is_connected=False
	producer = None
	while not is_connected:
		
		try:
			sleep(1)
			producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
			is_connected=True

		except Exception:
			print('error connecting')
			pass
	
	return producer

class TwitterSearchProducer():
    def __init__(self):
        self.stopFlag = False
        self.producer = get_producer()

    def stop(self):
        self.stopFlag = True

    def search(self, term):
        for status in api.GetStreamFilter(track=[term]):
            if 'text' in status:
                text = status['text']
                print(text)
                self.producer.send("kafkaesque", text.encode('utf-8'))
            if self.stopFlag:
                break


executor = ThreadPoolExecutor(2)
app = Flask(__name__)
socketio = SocketIO(app)
searchApi = TwitterSearchProducer()


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/search', methods=['POST'])
def search():
    global searchApi
    json_dict = request.get_json()
    if 'term' in json_dict:

        if searchApi is not None:
            searchApi.stop()
        searchApi = TwitterSearchProducer()

        # start producer with search term
        executor.submit(searchApi.search, json_dict['term'])

        session['query'] = json_dict['term']
        print('searching.. ', str(json_dict['term']))

    return ('', 200)


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)


@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))


# receives updates from the apache-spark consumer through websocket and feeds it to connected clients
@socketio.on('spark-update')
def handle_custom_event(jsonData):
    print('received custom event' + str(jsonData))
    socketio.emit('update', json.dumps(
        jsonData, ensure_ascii=False), room='feed')

# front-end subscribe to an update channel


@socketio.on('subscribe')
def handle_suscribe():
    join_room('feed')


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0",debug=True)
