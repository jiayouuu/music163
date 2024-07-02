import os
from pathlib import Path
import jieba.analyse
from snownlp import SnowNLP
import logging
SRC_PATH = Path(__file__).resolve().parents[2]
dict_txt_path = os.path.join(SRC_PATH, "txt", "dict.txt")
jieba.set_dictionary(dictionary_path=dict_txt_path)
jieba.setLogLevel(logging.INFO)
# 提取关键词
def get_keywords(content):
    jieba.del_word("首歌")
    return jieba.analyse.extract_tags(content)
# 获取情感倾向
def get_emotion(content):
    if content=="":
        return None
    return "%.2f" % SnowNLP(content).sentiments
