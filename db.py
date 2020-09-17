import os
from mysql.connector import MySQLConnection
import json
from glob import glob
from console import console
from colorama import Fore
from typing import Sequence
import traceback

# 将json文件录入mysql数据库
def importData(
    connect: MySQLConnection,
    source: str,
    table: str,
    path: str,
    dynasty: str,
    collection: str,
    author: str = None,
):
    names = tuple(glob(f"{source}/{path}"))
    console.log()
    begin = console.info(f"正在處理  {collection}")
    cursor = connect.cursor()
    success = 0
    error = 0
    for name in names:
        filename = os.path.basename(name)
        try:
            console.log(f"正在處理文件  {filename}")
            name = os.path.normpath(name)
            file = open(name, "r", encoding="utf-8")
            data = json.loads(file.read())
            if type(data).__name__ != "list":
                data = [data]
            for poet in data:
                if poet.get("author"):
                    author = poet["author"]
                sql = f"INSERT INTO `{table}` VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                if poet.get("paragraphs"):
                    paragraphs = json.dumps(poet.get("paragraphs"), ensure_ascii=False)
                else:
                    paragraphs = ""
                if poet.get("notes"):
                    notes = json.dumps(poet.get("notes"), ensure_ascii=False)
                else:
                    notes = ""
                if poet.get("content"):
                    content = json.dumps(poet.get("content"), ensure_ascii=False)
                else:
                    content = ""
                if poet.get("comment"):
                    comment = json.dumps(poet.get("comment"), ensure_ascii=False)
                else:
                    comment = ""
                if poet.get("tags"):
                    tags = json.dumps(poet.get("tags"), ensure_ascii=False)
                else:
                    tags = ""
                cursor.execute(
                    sql,
                    (
                        author,
                        dynasty,
                        poet.get("title") or "",
                        poet.get("rhythmic") or "",
                        poet.get("chapter") or "",
                        paragraphs,
                        notes,
                        collection,
                        poet.get("section") or "",
                        content,
                        comment,
                        tags,
                    ),
                )
                success += 1
        except Exception:
            console.error(traceback.format_exc())
            end = console.error(f"{filename}  處理出错")
            error += 1
    connect.commit()
    if error == 0:
        end = console.success(f"{collection}  處理完畢", begin)
    else:
        end = console.warning(f"{collection}  處理完畢，共有{error}个错误", begin)
    cursor.close()
    console.log()
    return {
        "collection": collection,
        "count": success,
        "time": f"{console.round(end - begin)}s",
    }


# 录入作者
def importAuthors(
    connect: MySQLConnection, source: str, table: str, paths: Sequence[str],
):
    names = ()
    for path in paths:
        names += tuple(glob(f"{source}/{path}"))
    console.log()
    begin = console.log("正在處理  作者", Fore.CYAN)
    cursor = connect.cursor()
    success = 0
    error = 0
    for name in names:
        name = os.path.normpath(name)
        filename = os.path.basename(name)
        try:
            console.log(f"正在處理文件  {filename}")
            file = open(name, "r", encoding="utf-8")
            data = json.loads(file.read())
            if type(data).__name__ != "list":
                data = [data]
            for author in data:
                sql = f"INSERT INTO `{table}` VALUES (null,%s,%s,%s)"
                cursor.execute(
                    sql,
                    (
                        author.get("name") or "",
                        author.get("desc") or author.get("description") or "",
                        author.get("short_description") or "",
                    ),
                )
                success += 1
        except Exception as e:
            console.error(traceback.format_exc())
            console.error(f"{filename}  處理出错")
            error += 1
    connect.commit()
    if error == 0:
        end = console.success("作者  處理完畢", begin)
    else:
        end = console.warning(f"作者  處理完畢，共有{error}个错误", begin)
    cursor.close()
    console.log()
    return {
        "collection": "作者",
        "count": success,
        "time": f"{console.round(end - begin)}s",
    }

