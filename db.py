import os
from mysql.connector import MySQLConnection
import json
from glob import glob
from console import console
from colorama import Fore
from typing import Sequence

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
    begin = console.log(f"正在處理  {collection}", Fore.CYAN)
    cursor = connect.cursor()
    count = 0
    try:
        for name in names:
            os.path.basename(name)
            console.log(f"正在處理文件  {os.path.basename(name)}")
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
                count += 1
                # break
        connect.commit()
        end = console.log(f"{collection}  處理完畢", Fore.GREEN, begin)
    except Exception as e:
        console.log(e)
        end = console.log(f"{collection}  處理出错", Fore.RED, begin)
        count = "失敗"
    finally:
        cursor.close()
        console.log()
        return {
            "collection": collection,
            "count": count,
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
    count = 0
    try:
        for name in names:
            name = os.path.normpath(name)
            console.log(f"正在處理文件  {os.path.basename(name)}")
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
                count += 1
                # break
        connect.commit()
        end = console.log("作者  處理完畢", Fore.GREEN, begin)
    except Exception as e:
        console.log(e)
        end = console.log("作者  處理出错", Fore.RED, begin)
        count = None
    finally:
        cursor.close()
        console.log()
        return {
            "collection": "作者",
            "count": count,
            "time": f"{console.round(end - begin)}s",
        }

