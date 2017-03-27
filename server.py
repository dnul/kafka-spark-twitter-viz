from flask import Flask,request,session
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



kafka = SimpleClient("localhost:9092")
api = twitter.Api(consumer_key='YnJhmBnBkaRY9KrIRoidA',
            consumer_secret='lAdMxNrYqKxWJ8mh8g79AYiUGIxnCqG2V3soOZnnwVM',
            access_token_key='556210107-2gQxW6J54wErB9t0YlqqfH6IZPCRgQa6rkTlMCc3',
            access_token_secret='ikjvynp1eZRoxRsdPtQPS4DpCigKxpHEN27RAFPU')
producer = KafkaProducer(bootstrap_servers='localhost:9092')


class TwitterSearchProducer():
    def __init__(self):
        self.stopFlag = False



    def stop(self):
        self.stopFlag=True

    def search(self,term):
        for status in api.GetStreamFilter(track=[term]):
            if 'text' in status:
                text = status['text']
                producer.send("kafkaesque",text.encode('utf-8'))
            if self.stopFlag:
                break;

executor = ThreadPoolExecutor(2)
app = Flask(__name__)
socketio = SocketIO(app)
future = None
searchApi = TwitterSearchProducer()




@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/search',methods=['POST'])
def search():
    global searchApi
    json_dict = request.get_json()
    print(json_dict['term'])
    if 'term' in json_dict:
        print(searchApi,'searchapi')
        if searchApi is not None:
           searchApi.stop()
        searchApi = TwitterSearchProducer()


        executor.submit(searchApi.search,json_dict['term'])


        session['query'] = json_dict['term']
        print('searching ',str(json_dict['term']))

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


# set the secret key.  keep this really secret:
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'





if __name__ == '__main__':
#	app.run(debug=True)
	socketio.run(app,debug=True)
