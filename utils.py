import json
import os
import re
import mysql.connector
import time
import math


# 将json文件录入mysql数据库
def importData(connect: mysql.connector.MySQLConnection, source: str, table: str, folder: str, pattern: str, dynasty: str, collection: str,  author: str = None):
    source += folder
    names = os.listdir(source)
    msg()
    begin = msg('正在處理  '+collection)
    cursor = connect.cursor()
    count = 0
    try:
        for name in names:
            match = re.match(re.compile(pattern), name)
            if match is not None:
                msg('正在處理文件  '+name)
                file = open(source+'/'+name, 'r', encoding='utf-8')
                data = json.loads(file.read())
                if type(data).__name__ != 'list':
                    data = [data]
                for poet in data:
                    if poet.get('author'):
                        author = poet['author']
                    sql = 'INSERT INTO {} VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(
                        table)
                    cursor.execute(sql, (
                        author,
                        dynasty,
                        poet.get('title') or '',
                        poet.get('rhythmic') or '',
                        poet.get('chapter') or '',
                        json.dumps(poet.get('paragraphs'), ensure_ascii=False) or '',
                        json.dumps(poet.get('notes'), ensure_ascii=False) or '',
                        collection,
                        poet.get('section') or '',
                        json.dumps(poet.get('content'), ensure_ascii=False) or '',
                        json.dumps(poet.get('comment'), ensure_ascii=False) or '',
                        json.dumps(poet.get('tags'), ensure_ascii=False) or ''
                    ))
                    count += 1
                # break
        connect.commit()
        end = msg(collection+'  處理完畢')
    except Exception:
        end = msg(collection+'  處理出错')
        count = None
    finally:
        cursor.close()
        msg()
        return {'count': count, 'time': getTimeString(begin, end)}


# 控制台输出信息
def msg(text: str = None):
    if text is None:
        text = ''.ljust(24, '-')
    t = time.time()
    now = time.localtime(t)
    h = str(now.tm_hour).zfill(2)
    m = str(now.tm_min).zfill(2)
    s = str(now.tm_sec).zfill(2)
    print('[{}:{}:{}] {}'.format(h, m, s, text))
    return t


# 格式化时间
def getTimeString(begin: float, end: float):
    h = 0
    m = 0
    s = math.ceil(end - begin)
    if s >= 60:
        m = int(s/60)
        s = s % 60
    if m >= 60:
        h = int(m/60)
        m = m % 60
    h = str(h).zfill(2)
    m = str(m).zfill(2)
    s = str(s).zfill(2)
    return '{}h{}m{}s'.format(h, m, s)
