import json

import mysql.connector
from colorama import Fore

from console import console
from db import importAuthors, importData


def start():
    console.logPath = "./log.txt"
    begin = console.log("開始處理文件", Fore.CYAN)

    # 获取各种参数
    configFile = open("./config.json", "r", encoding="utf-8")
    config = json.loads(configFile.read())
    table = config["table"]
    tableAuthor = config["tableAuthor"]
    source = config["source"]
    data = config["files"]["data"]
    include = config["files"]["include"]
    exclude = config["files"]["exclude"]
    authors = config["files"]["authors"]

    # 连接数据库
    connect = mysql.connector.connect(**config["mysql"])
    cursor = connect.cursor()
    cursor.execute("SET names 'utf8mb4'")

    # 删除旧表, 创建新表
    # 诗词表
    if len(table):
        cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
        sql = f"""CREATE TABLE `{table}` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`author` text DEFAULT NULL,
			`dynasty` text NOT NULL,
			`title` text DEFAULT NULL,
			`rhythmic` text DEFAULT NULL,
			`chapter` text DEFAULT NULL,
			`paragraphs` text NOT NULL,
			`notes` text DEFAULT NULL,
			`collection` text NOT NULL,
			`section` text DEFAULT NULL,
			`content` text DEFAULT NULL,
			`comment` text DEFAULT NULL,
			`tags` text DEFAULT NULL,
			PRIMARY KEY (`id`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"""
        cursor.execute(sql)
    # 作者表
    if len(tableAuthor):
        cursor.execute(f"DROP TABLE IF EXISTS `{tableAuthor}`")
        sql = f"""CREATE TABLE `{tableAuthor}` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`name` varchar(100) NOT NULL,
			`description` text,
			`short_description` text,
			PRIMARY KEY (`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"""
        cursor.execute(sql)

    cursor.close()

    # 循环处理json文件
    arr = []
    maxLenCollection = 0
    maxLenTime = 0
    total = 0
    res = None
    hasInclude = len(include) > 0
    hasExclude = len(exclude) > 0
    if len(table):
        for info in data:
            if hasInclude and info["collection"] not in include:
                continue
            if hasExclude and info["collection"] in exclude:
                continue
            res = importData(connect, source, table, info)
            arr.append(res)
            maxLenCollection = max(maxLenCollection, console.strLen(res["collection"]))
            maxLenTime = max(maxLenTime, console.strLen(res["time"]))
            if isinstance(res["count"], int):
                total += res["count"]
    if len(tableAuthor):
        res = importAuthors(connect, source, tableAuthor, authors)
        arr.append(res)
        maxLenCollection = max(maxLenCollection, console.strLen(res["collection"]))
        maxLenTime = max(maxLenTime, console.strLen(res["time"]))
        if isinstance(res["count"], int):
            total += res["count"]
    connect.commit()
    connect.close()

    # 最后输出统计信息
    end = console.log("所有文件處理完畢", Fore.GREEN, begin)
    console.log()
    for v in arr:
        collection = console.strAlign(v["collection"], maxLenCollection, "L")
        time = console.strAlign(v["time"], maxLenTime, "L")
        console.log(f"{collection}  用時：{time}  記錄數：{v['count']}")
    console.log(f"共計用時：{console.round(end-begin)}s")
    console.log(f"記錄總數：{total}")
    console.log()


if __name__ == "__main__":
    start()
