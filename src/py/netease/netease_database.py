import mysql.connector
from pathlib import Path
from ..utils import readproperties as rp
import os

SRC_PATH = Path(__file__).resolve().parents[2]
conf_path = os.path.join(SRC_PATH, "conf.properties")


# 链接数据库
def get_connection():
    conf = rp.read_all(conf_path, "mysql")
    try:
        return mysql.connector.connect(
            host=conf["host"],
            port=conf["port"],
            user=conf["user"],
            password=conf["password"],
        )
    except mysql.connector.errors.DatabaseError:
        print("connect mysql err")


# 插入数据
def insert(database: str, table: str, columns: tuple, values: list[tuple]):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    placeholder = ",".join(["%s"] * len(columns))
    columns = ",".join(columns)
    sql = f"insert into `{table}` ({columns}) values ({placeholder})"
    cursor = conn.cursor()
    cursor.executemany(sql, values)
    conn.commit()
    cursor.close()
    conn.close()


# 查询数据
def query(database: str, table: str, columns: tuple, requirement: str = ""):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    columns = ",".join(columns)
    sql = f"select {columns} from `{table}` {requirement}"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


# 更新数据
def update(database: str, table: str, columns: tuple, requirement: str, values: tuple):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    temp = []
    for c in columns:
        c += "= %s"
        temp.append(c)
    columns = ",".join(temp)
    sql = f"update `{table}` set {columns} {requirement}"
    cursor = conn.cursor()
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()


# 删除数据
def delete(database: str, table: str, requirement: str):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    sql = f"delete from `{table}`  {requirement}"
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()


# 创建数据库
def create_database(name):
    sql = f"CREATE DATABASE IF NOT EXISTS {name} CHARACTER SET utf8mb4;"
    conn = get_connection()
    if conn.is_connected():
        conn._execute_query(sql)
        conn.close()


# 删除数据库
def delete_database(name):
    sql = f"drop database {name}"
    conn = get_connection()
    if conn.is_connected():
        conn._execute_query(sql)
        conn.close()


# 创建表
def create_table(database, table):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    conn._execute_query(table)
    conn.close()


# 查询表是否存在
def query_table(database, table):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    cursor = conn.cursor()
    sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{database}' AND table_name = '{table}'"
    cursor.execute(sql)
    result = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return True if result > 0 else False


# 清空表
def delete_table(database, table):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    sql = f"truncate table `{table}`"
    conn._execute_query(sql)
    conn.close()


# 删除表
def drop_table(database, table):
    conn = get_connection()
    conn._execute_query(f"use {database}")
    sql = f"drop table `{table}`"
    conn._execute_query(sql)
    conn.close()
