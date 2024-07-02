from flask import Flask, request
import json
from flask_cors import CORS
from py.netease.netease_database import get_connection
from py.netease.request_netease import get_songs

app = Flask(__name__)
CORS(app)


def union_query(database: str, columns: tuple, requirement: str = ""):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    cursor = conn.cursor()
    cursor.execute("show tables")
    result = cursor.fetchall()
    tables = [r[0] for r in result]
    columns = ",".join(columns)
    sql=' union '.join([f'select {columns} from `{table}` {requirement}' for table in tables])
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_info(category):
    id = request.get_json()["id"]
    return json.loads(
        union_query("songs", (f"{category}",), f"where song_id ={id}")[0][0]
    )


@app.route("/api/commentsinfo/keywords", methods=["POST"])
def get_keywords():
    return {"keywords": get_info("keywords")}


@app.route("/api/commentsinfo/hour_minute", methods=["POST"])
def get_hour_minute():
    return {"hour_minute": get_info("comment_hour_minute")}


@app.route("/api/commentsinfo/location", methods=["POST"])
def get_location():
    return {"location": get_info("location")}


@app.route("/api/commentsinfo/platform", methods=["POST"])
def get_platform():
    return {"platform": get_info("platform")}


@app.route("/api/commentsinfo/generation", methods=["POST"])
def get_generation():
    return {"generation": get_info("generation")}


@app.route("/api/commentsinfo/gender", methods=["POST"])
def get_gender():
    return {"gender": get_info("gender")}


@app.route("/api/commentsinfo/emotion", methods=["POST"])
def get_emotion():
    return {"emotion": get_info("emotion")}


@app.route("/api/songs/getsong", methods=["POST"])
def get_song():
    name = request.get_json()["name"]
    return {"songslist": get_songs(search=name)}


@app.route("/api/songs/isvalid", methods=["POST"])
def is_valid():
    id = request.get_json()["id"]
    data = union_query("songs", ("*",), f"where song_id = {id}")
    flag = True
    if len(data) == 0:
        flag = False
    elif data[0][2] == 0 or data[0][3] == 0:
        flag = False
    return {"isvalid": "yes" if flag == True else "no"}


if __name__ == "__main__":
    app.run(port=9000, debug=True)
