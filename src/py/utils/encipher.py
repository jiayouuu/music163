from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base64 import b64encode
from random import random
from math import floor
import os
from pathlib import Path
import execjs
from . import key
# 实现AES-CBC加密
def encrypt_aes(text, key, iv):
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    padded_text = pad(text.encode("utf-8"), AES.block_size)
    ciphertext = cipher.encrypt(padded_text)
    return b64encode(ciphertext).decode("utf-8")
# 仿照原b函数构造加密函数
def enc(a, b):
    c = b
    d = "0102030405060708"
    e = a
    f = encrypt_aes(e, c, d)
    return f
# 获取随机16位字符串
def randstr(length):
    s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    res = ""
    temp = 0
    for i in range(1, length + 1):
        temp = floor(random() * len(s))
        res += s[temp]
    return res
# 读取js文件夹中加密函数
SRC_PATH = Path(__file__).resolve().parents[2]
js_encipher_path = os.path.join(SRC_PATH, "js", "encipher.js")
encipher_js = execjs.compile(
    open(file=js_encipher_path, mode="r", encoding="utf-8").read()
)
# 包装js加密函数加密
def enc_key(randstr):
    return encipher_js.call("enc", randstr, key.ks1, key.ks2)


