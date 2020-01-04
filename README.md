# 古诗词自动录入数据库(mysql)

## 运行环境

python 3

python依赖: mysql-connector-python

## config.json 说明

```jsonc
"mysql": {
    "host": "127.0.0.1",            // 服务器地址
    "user": "root",                 // 用户名
    "password": "123456",           // 密码
    "port": "3306",                 // 端口
    "database": "test",             // 数据库名字
},
"table": "chinese_poetry"       // 表名 !!!注意, 若表名已存在会删除该表, 请注意备份!
"source": "/opt/chinese-poetry",   	// 古诗词根目录
"files": {
    "data": [                                // 录入数据的参数, 你可以根据需要修改或删除部分内容
        {
            "folder": "/youmengying",        // 指定文件夹
            "pattern": "youmengying.json",   // 指定匹配json文件(正则)
            "dynasty": "清",                 // 指定朝代
            "collection": "幽夢影",          // 指定集合
            "author": "张潮"                 // 可选, 手动指定作者
        }
    ],
    "include": ["唐詩", "宋詞"],			// 只处理特定的collection
    "exclude": ["幽夢影"]					// 不处理特定的collection, 若include不为空, 则此项无效
}
```

## 使用方法

> 1. 前往下载 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry.git)

> 2. 将 ```config.json.sample``` 另存为 ```config.json``` 并配置好相关参数

> 3. 运行 ```start.py```

## FAQ

> 暂无


