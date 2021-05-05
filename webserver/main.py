#!/usr/bin/python3

import flask
from flask_socketio import SocketIO, send, join_room
from flask import request, jsonify, redirect, send_file
from flask_cors import CORS, cross_origin
import json
import uuid
import pandas as pd
from os import listdir
from os.path import isfile, join
import random

from twitter_service import TwitterService
from folder_service import FolderService
from meme_service import MemeService
from visualize_service import VisualizerService
from flood_service import FloodService

from pipeline import Pipeline

DEBUG = True

app = flask.Flask(__name__)
app.config["DEBUG"] = DEBUG

socketio = SocketIO(app, cors_allowed_origins="*")

sql_data = "./data/db.sqlite"

service_active = []

service_available = [FolderService(id="folder", name="Images from folder"),
                     TwitterService(id="twitter", name="Twitter crawler", db="./data/db.sqlite", table_name="raw_tweets"),
                     MemeService(name="Meme Filter", table_name="memes", id="meme", db="./data/db.sqlite"),
                     FloodService(name="Flood Filter", table_name="flood", id="flood", db="./data/db.sqlite"),
                     VisualizerService(name="Visualizer", id="visu")]

PIPELINE = Pipeline(service_active, service_available)

@app.route("/update", methods=["POST", "GET"])
@cross_origin()
def update_pipeline():
    PIPELINE.update(request.data)
    return jsonify({ "status": "ok" })

@app.route("/pipeline")
@cross_origin()
def get_pipeline():
    print(PIPELINE.get_all_service_json())
    return jsonify(PIPELINE.get_all_service_json())

@app.route("/images/<id>")
@cross_origin()
def get_image(id):
    return send_file("data/images/" + id)

# get the images after the service has processsed them
@app.route("/<service_id>/out")
@cross_origin()
def get_out_images(service_id):
    images = PIPELINE.get_service(service_id).get_images()
    random.shuffle(images)
    link = ["http://localhost:8080/images/" + i for i in images[:5]]
    print("ICICICIC", link)
    return jsonify(link)

# get the images comming in the service
@app.route("/<service_id>/in")
@cross_origin()
def get_comming_images(service_id):
    if request.args.get("size"):
        size = int(request.args.get("size"))
    else:
        size = 5
    images = PIPELINE.get_comming_images(service_id)
    random.shuffle(images)
    link = ["http://localhost:8080/images/" + i for i in images[:size]]
    return jsonify(link)

@app.route("/")
def index_page():
    if DEBUG:
        return redirect("http://localhost:3000/")
    else:
        print("todo")

@app.route("/<service_name>", methods=["POST", "GET"])
@cross_origin()
def service_page(service_name):
    if request.method == "POST":
        body = json.loads(request.data)
        service = PIPELINE.get_service(service_name)
        service.set_args(body)

        return { "service": service.dumps() }

@app.route("/socket")
@cross_origin()
def run_service():
    room_id = uuid.uuid4()
    return { "socket": room_id }

# when we want to run a service
@socketio.on('join')
def on_join(data):
    room = data['room']
    service = data["service"]
    join_room(room)

    # twitter is a special process because it doesnt use input 
    if service == "twitter":
        service = PIPELINE.get_service("twitter")
        service.set_room(room)
        service.run()
    else:
        PIPELINE.run_service(data["service"], room)

if __name__ == "__main__":
    print("ici")
    socketio.run(app)
    app.run(port=8080)
    


