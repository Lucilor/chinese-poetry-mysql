import json
import mysql.connector
from utils import importData, msg, getTimeString


def start():
    begin = msg('開始處理文件')

    # 获取各种参数
    configFile = open('./config.json', 'r', encoding='utf-8')
    config = json.loads(configFile.read())
    table = config['table']
    source = config['source']
    data = config['files']['data']
    include = config['files']['include']
    exclude = config['files']['exclude']

    # 连接数据库
    connect = mysql.connector.connect(**config['mysql'])

    # 删除旧表, 创建新表
    cursor = connect.cursor()
    cursor.execute('DROP TABLE IF EXISTS {}'.format(table))
    sql = '''CREATE TABLE {} (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `author` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `dynasty` text COLLATE utf8mb4_unicode_ci NOT NULL,
        `title` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `rhythmic` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `chapter` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `paragraphs` text COLLATE utf8mb4_unicode_ci NOT NULL,
        `notes` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `collection` text COLLATE utf8mb4_unicode_ci NOT NULL,
        `section` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `content` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `comment` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `tags` text COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'''
    cursor.execute(sql.format(table))

    # 循环处理json文件
    arr = []
    l = 0
    count = 0
    for d in data:
        if len(include) and d['collection'] not in include:
            continue
        if len(exclude) and d['collection'] in exclude:
            continue
        res = importData(connect, source, table, d['folder'],
                         d['pattern'], d['dynasty'], d['collection'])
        l = max(l, len(d['collection']))
        arr.append({'collection': d['collection'], 'time': res['time']})
        count += res['count']
    cursor.close()
    connect.close()

    # 最后输出统计信息
    end = msg('所有文件處理完畢, 記錄總數: '+str(count))
    msg()
    for v in arr:
        msg('{}  用時  {}'.format(v['collection'].ljust(
            l+l-len(v['collection'])), v['time']))
    msg('共計用時  '+getTimeString(begin, end))
    msg()


start()
