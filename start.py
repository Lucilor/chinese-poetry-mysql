import json
import mysql.connector
from utils import importData, importAuthors, msg, getTimeString


def start():
	begin = msg('開始處理文件')

	# 获取各种参数
	configFile = open('./config.json', 'r', encoding='utf-8')
	config = json.loads(configFile.read())
	table = config['table']
	tableAuthor = config['tableAuthor']
	source = config['source']
	data = config['files']['data']
	include = config['files']['include']
	exclude = config['files']['exclude']
	authors = config['files']['authors']

	# 连接数据库
	connect = mysql.connector.connect(**config['mysql'])

	# 删除旧表, 创建新表
	# 诗词表
	cursor = connect.cursor()
	if len(table):
		cursor.execute('DROP TABLE IF EXISTS `{}`'.format(table))
		sql = '''CREATE TABLE `{}` (
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
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'''
		cursor.execute(sql.format(table))
	# 作者表
	if len(tableAuthor):
		cursor.execute('DROP TABLE IF EXISTS `{}`'.format(tableAuthor))
		sql = '''CREATE TABLE `{}` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`name` varchar(100) NOT NULL,
			`description` text,
			`short_description` text,
			PRIMARY KEY (`id`)
			) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
		cursor.execute(sql.format(tableAuthor))

	# 循环处理json文件
	arr = []
	l = 0
	total = 0
	if len(table):
		for d in data:
			if len(include) and d['collection'] not in include:
				continue
			if len(exclude) and d['collection'] in exclude:
				continue
			res = importData(connect, source, table,
							d['path'], d['dynasty'], d['collection'])
			l = max(l, len(d['collection']))
			if res['count'] is None:
				arr.append({'collection': d['collection'],
						'time': res['time'], 'count': '失敗'})
			else:
				arr.append(
					{'collection': d['collection'], 'time': res['time'], 'count': res['count']})
				total += res['count']
	if len(tableAuthor):
		res = importAuthors(connect, source, tableAuthor, authors)
	if res['count'] is None:
		arr.append(
			{'collection': '作者', 'time': res['time'], 'count': '失敗'})
	else:
		arr.append(
			{'collection': '作者', 'time': res['time'], 'count': res['count']})
		total += res['count']
	connect.close()

	# 最后输出统计信息
	end = msg('所有文件處理完畢, 記錄總數: '+str(total))
	msg()
	for v in arr:
		msg('{}  用時  {}  {}'.format(v['collection'].ljust(
			l+l-len(v['collection'])), v['time'], v['count']))
	msg('共計用時  '+getTimeString(begin, end))
	msg()


start()
