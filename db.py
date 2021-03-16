import os
from mysql.connector import MySQLConnection
import json
from glob import glob

from mysql.connector.cursor import MySQLCursor
from console import console
from colorama import Fore
from typing import Dict, Iterable
import traceback

fields = {
    "author": {"type": "string"},
    "dynasty": {"type": "string"},
    "title": {"type": "string"},
    "rhythmic": {"type": "string"},
    "chapter": {"type": "string"},
    "paragraphs": {"type": "json"},
    "notes": {"type": "json"},
    "collection": {"type": "string"},
    "section": {"type": "string"},
    "content": {"type": "json"},
    "comment": {"type": "json"},
    "tags": {"type": "json"},
}

# 将json文件录入mysql数据库
def importData(connect: MySQLConnection, source: str, table: str, info: Dict):
    path = info["path"]
    dynasty = info["dynasty"]
    collection = info["collection"]
    author = info.get("author")
    names = tuple(glob(f"{source}/{path}"))
    console.log()
    begin = console.info(f"正在處理  {collection}")
    cursor: MySQLCursor = connect.cursor()
    success = 0
    error = 0
    for name in names:
        filename = os.path.basename(name)
        try:
            console.log(f"正在處理文件  {filename}")
            name = os.path.normpath(name)
            file = open(name, "r", encoding="utf-8")
            data = json.loads(file.read())
            if filename == "tangshisanbaishou.json":
                data = shisanbai(data)
            if type(data).__name__ != "list":
                data = [data]
            for poet in data:
                values = []
                for field in fields:
                    if fields[field]["type"] == "string":
                        value = poet.get(field, "")
                        if field == "collection":
                            value = collection
                        elif field == "dynasty":
                            value = dynasty
                        elif field == "author":
                            if author:
                                value = author
                            if not value:
                                value = "不詳"
                        values.append(value)
                    else:
                        value = poet.get(field, None)
                        if field == "tags":
                            if type(value) != list:
                                try:
                                    value = list(value)
                                except:
                                    value = []
                            if collection not in value:
                                value.append(collection)
                        values.append(json.dumps(value, ensure_ascii=False))
                sql = f"INSERT INTO `{table}` VALUES (null,{','.join(map(lambda _:'%s',values))})"
                cursor.execute(sql, values)
                success += 1
        except Exception:
            console.error(traceback.format_exc())
            end = console.error(f"{filename}  處理出错")
            error += 1
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
    connect: MySQLConnection,
    source: str,
    table: str,
    paths: Iterable[str],
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


# 特殊处理唐诗三百首
def shisanbai(data: Dict):
    content = data["content"]
    data["dynasty"] = "唐"
    result = []
    for group in content:
        for poet in group["content"]:
            if poet["subchapter"]:
                poet["title"] = poet["subchapter"]
            else:
                poet["title"] = poet["chapter"]
            del poet["chapter"]
            del poet["subchapter"]
            poet["tags"] = ["唐詩三百首", group["type"]]
            result.append(poet)
    return result
