import time
import requests
import json
from multiprocessing import Queue as pq 
from bs4 import BeautifulSoup
import re
from ..utils import encipher,key
# 加密两次请求参数
def enc_text(query, randstr):
    return encipher.enc(encipher.enc(json.dumps(query), key.ks3), randstr)


# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


# 获取一首歌的全部评论，count为获取数量，不建议获取太多
#
def get_comments_all(id, queue: pq, count=50, onece=50, proxies={}):
    # if isinstance(queue, Queue) != True:
    #     raise Exception("queue typeErr")
    if count < onece:
        raise Exception("count must be bigger than onece")
    stime = time.time()
    cursor = -1
    total = count
    page_count = divmod(total, onece)[0]
    last_size = divmod(total, onece)[1]
    randstr16 = encipher.randstr(16)
    key = {"randstr16": randstr16, "enc_key": encipher.enc_key(randstr16)}
    print("第1次爬取:", end="")

    try:
        res = get_comments_once(id=id, key=key, pageSize=onece, proxies=proxies)
    except Exception as e:
        print(e)
    else:
        print(f'成功获取{len(res["comments"])}条！')
        queue.put([comment_parse(comment=comment) for comment in res["comments"]])
        cursor = res["cursor"]
        total = res["totalCount"]
        if count > total:
            page_count = divmod(total, onece)[0]
            last_size = divmod(total, onece)[1]
            if onece >= total:
                print(f"爬取完成！共爬取{total}条")
                return
        elif onece == count:
            print(f"爬取完成！共爬取{onece}条")
            return
        else:
            print(f"当前共爬取{onece}条！")
    for i in range(2, page_count + 1):
        gtime = time.time()
        if gtime - stime > 30:
            randstr16 = encipher.randstr(16)
            key = {"randstr16": randstr16, "enc_key": encipher.enc_key(randstr16)}
            stime = gtime

        print(f"第{i}次爬取:", end="")
        try:
            res = get_comments_once(
                id=id, key=key, pageNo=i, pageSize=onece, cursor=cursor, proxies=proxies
            )
        except Exception as e:
            print(e)
        else:
            print(f"成功获取{onece}条！")
            if i == page_count and last_size == 0:
                print(f"爬取完成！共爬取{onece*i}条")
            else:
                print(f"当前共爬取{i*onece}条！")
                cursor = res["cursor"]
            queue.put([comment_parse(comment=comment) for comment in res["comments"]])
    if last_size != 0:
        print(f"第{page_count+1}次爬取:", end="")
        try:
            res = get_comments_once(
                id=id,
                key=key,
                pageNo=(page_count + 1),
                pageSize=last_size,
                cursor=cursor,
                proxies=proxies,
            )
        except Exception as e:
            print(e)
        else:
            print(f"成功获取{last_size}条！")
            print(f"爬取完成！共爬取{page_count*onece+last_size}条")
            queue.put([comment_parse(comment=comment) for comment in res["comments"]])

# 解析。。。
def comment_parse(comment):
    return {
        "commentId": comment["commentId"],
        "content": re.sub(r"\s|\'|\"", "", comment["content"],),
        "commentTime": int(comment["time"]/1000),
        "userId": comment["user"]["userId"],
        "ipLocation": comment["ipLocation"]["location"],
        'platform':(None if 'endpoint' not in comment['extInfo'] else comment["extInfo"]["endpoint"]["OS_TYPE"])
    }


# 获取歌曲评论一次，默认获取50条
def get_comments_once(
    id,
    key,
    pageNo=1,
    cursor=-1,
    pageSize=50,
    offset=0,
    orderType=1,
    token="",
    proxies={},
):

    url = (
        f"https://music.163.com/weapi/comment/resource/comments/get?csrf_token={token}"
    )
    params = {
        "csrf_token": f"{token}",  # 可以为空值
        "cursor": f"{cursor}",
        "offset": f"{offset}",
        "orderType": f"{orderType}",
        "pageNo": f"{pageNo}",
        "pageSize": f"{pageSize}",  # 评论数
        "rid": f"R_SO_4_{id}",  # 歌曲编号
        "threadId": f"R_SO_4_{id}",  # 歌曲编号
    }
    # 包装data
    data = {
        # 两次加密
        "params": enc_text(params, key["randstr16"]),
        "encSecKey": key["enc_key"],
    }

    # 返回json格式返回值
    res = requests.post(url, data=data, headers=headers, proxies=proxies).json()
    code = res["code"]
    comments = res["data"]["comments"]
    if code == 200 and len(comments) != 0:
        return {
            "totalCount": res["data"]["totalCount"],
            "cursor": res["data"]["cursor"],
            "comments": comments,
        }
    else:
        raise Exception("request comments err")


# 获取用户信息
def get_userinfo(userId, proxies={}):
    url = f"https://music.163.com/api/v1/user/detail/{userId}"
    res = requests.get(url=url, headers=headers, proxies=proxies)
    if res.status_code == 200:
        if  'profile' not in res.json():
            return None
        res = res.json()["profile"]
        return {
            "userId": res["userId"],
            "nickname": res["nickname"],
            "birthday": int(res["birthday"]/1000) if 0<int(res["birthday"]/1000)<int(time.time()) else 0,
            "gender": res["gender"],
            "cityCode": res["city"],
        }
    else:
        raise Exception("request userInfo err")


# 输入歌曲名，返回歌曲列表
def get_songs(search, limit=10, proxies={}):
    url = f"https://music.163.com/api/search/get?s={search}&type=1&limit={limit}"
    res = requests.get(url=url, headers=headers, proxies=proxies)
    if res.status_code == 200:
        res = res.json()["result"]["songs"]
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "artists": {
                    "id": r["artists"][0]["id"],
                    "name": r["artists"][0]["name"],
                },
                "album": {"id": r["album"]["id"], "name": r["album"]["name"]},
            }
            for r in res
        ]
    else:
        raise Exception("request song err")





# 获取榜单列表
def get_songslist(listId=3778678, proxies={}):
    url = f"https://music.163.com/discover/toplist?id={listId}"
    res = requests.get(url=url, headers=headers, proxies=proxies)
    if res.status_code != 200:
        raise Exception("request songslist err")
    soup = BeautifulSoup(res.text, "html.parser")
    liList = soup.select("ul[class='f-hide'] li a")
    result = []
    for i in liList:
        result.append({"id": i.attrs["href"][9:], "name": i.string})
    return result


#1397662832
# get_comments_all(id=2124385868, count=21, onece=10)
# res=get_songs("又见炊烟")
# print(res)

# ————————————————————————————————————————————————————————————————————————————
# url="https://music.163.com/weapi/cloudsearch/get/web?csrf_token="
# params={
#     "csrf_token": "",
#     'hlposttag': "</span>",
#     'hlpretag': "<span class=\"s-fc7\">",
#     'id': "4972962188",
#     'limit': "30",
#     'offset': "0",
#     's': "奢香夫人",
#     'total': "true",
#     'type': "1"
# }
# print(get(url,params))
# {'code': 50000005}
# 歌曲搜索建议/加密
# url = "https://music.163.com/weapi/search/suggest/web?csrf_token="
# song = {"s": "又见炊烟", "limit": "20", "csrf_token": ""}
# 歌曲搜索
# https://music.163.com/api/search/get?s='又见炊烟'&type=1&limit=3
# 用户信息
# https://music.163.com/api/v1/user/detail/1661226615
####################################################
