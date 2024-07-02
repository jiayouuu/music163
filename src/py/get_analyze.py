from .netease import request_netease as rn
from .netease import netease_database as db
from multiprocessing import Queue as pq
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import  Process
from .utils import handing
import re
import time
from .utils import tablestruct as tb
from .utils import analyze as al

# 创建数据库
db.create_database("songs")
db.create_database("comments")
# 榜单类别
top_list = [
    {"type": "hot", "id": 3778678},
    {"type": "soaring", "id": 19723756},
    {"type": "new", "id": 3779629},
    {"type": "original", "id": 2884035},
]


def handing_content(content_lsit: list):
    result = []
    for content in content_lsit:
        keywords = handing.get_keywords(content[0])
        emotion = handing.get_emotion(content[0])
        result.append(
            {"commentId": content[1], "keywords": keywords, "emotion": emotion}
        )
    return result


def handing_user(userId_list: list):
    with ThreadPoolExecutor() as pool:
        user_info_futures = pool.map(rn.get_userinfo, userId_list)
        return [future for future in user_info_futures]


def handing_data(queue: pq, table_name):
    with ProcessPoolExecutor() as pool:
        while True:
            data = queue.get()
            if data is None:
                break
            future_content = pool.submit(
                handing_content, [(d["content"], d["commentId"]) for d in data]
            )
            future_user = pool.submit(handing_user, [d["userId"] for d in data])
            content_info = future_content.result()
            user_info = future_user.result()
            values = []
            for d, c, u in zip(data, content_info, user_info):
                values.append(
                    (
                        d["commentId"],
                        d["content"],
                        d["commentTime"],
                        d["userId"],
                        d["ipLocation"],
                        d["platform"],
                        u["nickname"] if u !=None else None,
                        u["birthday"] if u !=None else 0,
                        ("male" if u["gender"] == 1 else "female") if u!=None else None,
                        u["cityCode"] if u!=None else 0,
                        ("/".join(c["keywords"])) if u!=None else None,
                        c["emotion"],
                    )
                )
            db.insert(
                "comments",
                table_name,
                (
                    "comment_id",
                    "comment_content",
                    "comment_time",
                    "user_id",
                    "location",
                    "platform",
                    "nickname",
                    "birthday",
                    "gender",
                    "city_code",
                    "keyword",
                    "emotion",
                ),
                values,
            )


def init_db(toplist: int):
    # 指定热歌榜
    category = top_list[toplist]
    # 创建数据表
    db.create_table("songs", tb.songs_sql.format(name=category["type"]))
    # 爬取榜单列表
    new_songs_list = rn.get_songslist(category["id"])
    # 查询数据库已有列表
    exists_songs_list = db.query("songs", category["type"], ("song_id",))
    # 获取需要插入数据库的列表
    insert_list = [
        song
        for song in new_songs_list
        if song["id"] not in [id[0] for id in exists_songs_list]
    ]
    # 插入
    db.insert(
        "songs",
        category["type"],
        ("song_id", "song_name"),
        [(song["id"], re.sub(r"\s|\'|\"", "", song["name"])) for song in insert_list],
    )


def get_all(toplist: int, songslength: int, commentslength: int, onece: int = 50):
    init_db(toplist)
    # 指定热歌榜
    category = top_list[toplist]
    # 查询需要更新的歌曲列表，3天一更新
    songs = db.query(
        "songs",
        category["type"],
        ("song_id", "song_name"),
        "where TIMESTAMPDIFF(DAY, FROM_UNIXTIME(update_time), CURRENT_DATE) > 3",
    )
    for song in songs[:songslength]:
        queue = pq(maxsize=10)
        song_id = song[0]
        # 去除引号，空格
        song_name = re.sub(r"\s|\'|\"", "", song[1])
        table_name = song_name + "_" + song_id
        is_exists = db.query_table("comments", table_name)
        if is_exists == True:
            db.delete_table("comments", table_name)
        else:
            db.create_table("comments", tb.comments_sql.format(name=table_name))
        process_request = Process(
            target=rn.get_comments_all, args=(song_id, queue, commentslength, onece)
        )
        process_handing = Process(target=handing_data, args=(queue, table_name))
        print(f"当前爬取第{songs.index(song) + 1}首歌，{table_name}")
        process_request.start()
        process_handing.start()
        db.update(
            "songs",
            category["type"],
            ("update_time", "is_completed"),
            f"where song_id = {song_id}",
            (int(time.time()), 0),
        )
        process_request.join()
        queue.put(None)
        print('正在处理······')
        process_handing.join()
        print('正在存储······')
        data = al.analyze("comments", table_name)
        db.update(
            "songs",
            category["type"],
            (
                "is_completed",
                "comment_hour_minute",
                "location",
                "platform",
                "generation",
                "gender",
                "keywords",
                "emotion",
            ),
            f"where song_id = {song_id}",
            (
                1,
                data["comment_hour_minute"],
                data["location"],
                data["platform"],
                data["generation"],
                data["gender"],
                data["keywords"],
                data["emotion"],
            ),
        )
        print('完成！')
