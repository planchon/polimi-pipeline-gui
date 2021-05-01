import os.path
import json
from flask_socketio import SocketIO, send, join_room
import pandas as pd
import sqlite3 as sq

class Service:
    name = ""
    args = {}
    errors = {}
    db_path = None
    table_name = ""
    room = 0

    IMAGE_FOLDER = "data/images"

    def __init__(self, name="", id="", db=None, table_name=""):
        self.name = name
        self.id = id
        self.db_path = db
        self.table_name = table_name

        self.setup()

    def setup(self):
        pass

    def set_room(self, room):
        self.room = room

    def send(self, message, type="console"):
        if self.room == 0:
            raise "Socket not setup"

        send({"service": self.name, "type": type, "message": message}, to=self.room)

    def dumps(self):
        return {
            "name": self.name,
            "args": self.args
        }

    def add_accepted_images(self, data):
        _tmp = []
        for x in data:
            _tmp.append("http://localhost:8080/images/" + x["image"])
        
        self.send(json.dumps(_tmp), type="image")
        conn = sq.connect(self.db_path)
        df = pd.DataFrame(data)
        df.to_sql(self.table_name, conn, if_exists="append", index=False)
        conn.commit()
        conn.close()

    def get_images(self):
        conn = sq.connect(self.db_path)
        df = pd.read_sql_query('SELECT * FROM ' + self.table_name, conn)
        print(df)
        return df["image"]

    def set_data_provider(self, table_name):
        self.data_provider = table_name

    def set_args(self, args):
        self.args = args

    def run(self):
        pass

    def output(self):
        pass