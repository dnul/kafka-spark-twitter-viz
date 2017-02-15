from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import join_room, leave_room


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def hello_world():
    return render_template("index.html")

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('customevent')
def handle_custom_event(json):
	print('received custom event' + str(json))
	socketio.emit('update',str(json),room='feed')

@socketio.on('subscribe')
def handle_suscribe():
	join_room('feed')

	




if __name__ == '__main__':
#	app.run(debug=True)
	socketio.run(app,debug=True)
