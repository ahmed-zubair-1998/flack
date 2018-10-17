import os
import requests

from collections import deque
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config.from_mapping(
    SECRET_KEY='dev'
)
socketio = SocketIO(app)

users = {}
rooms = {}

dq = deque(maxlen = 100)
rooms["general"] = dq

@app.route("/login", methods=('GET', 'POST'))
def login():
    if request.method == "POST":
        username = request.form["username"]
        session.clear()
        session['username'] = username
        if username not in users:
            users[username] = ''
        return redirect(url_for('chat', room="general"))
    return render_template("login.html")
        

@app.route("/", methods=('GET', 'POST'))
def index():
    if session.get('username') is None:
        return redirect(url_for('login'))
    if request.method == "POST":
        if "new_room" in request.form:
            rooms[request.form["new_room"]] = deque(maxlen = 100)
        if "room" in request.form:
            room=request.form["room"]
            return redirect(url_for('chat', room=room))
        if "user" in request.form:
            room=users[request.form["user"]]
            return redirect(url_for('chat', room=room))

    return render_template("index.html", users=users.keys(), rooms=rooms.keys())


@app.route("/chat/<string:room>", methods=('GET', 'POST'))
def chat(room):
    if request.method == "POST":
        return redirect(url_for('index'))
    if room not in rooms:
        return render_template("chat.html", room=room)
    return render_template("chat.html", room=room, messages=rooms[room])    

@socketio.on("on connect")
def onConnect():
    username = session['username']
    users[username] = request.sid


@socketio.on("join")
def on_join(data):
    username = session['username']
    room = data['room'].split('/')[-1]
    join_room(room)
    message = username + ' has joined the room'
    emit("message recieved", {"message": message}, broadcast=True, room=room)


@socketio.on("leave")
def on_leave(data):
    username = session['username']
    room = data['room'].split('/')[-1]
    leave_room(room)
    message = username + ' has left the room'
    emit("message recieved", {"message": message}, broadcast=True, room=room)

    
@socketio.on("send message")
def Send(data):
    message = session['username'] + ': ' + data["message"]
    room = data['room'].split('/')[-1]
    if room in rooms:
        rooms[room].append(message)
    emit("message recieved", {"message": message}, broadcast=True, room=room)
