# 项目介绍

* 基于Django的个人博客(https://github.com/2675hujilo/DjangoBlog)
* 使用的语言:Python，HTML，CSS
* 使用到的工具:Django框架、Redis缓存数据库、MySQL数据库、Celery任务队列，CKEditor富文本编辑器
* 数据库包含用戶表、分类表、文章表、评论表，网站信息表，网站链接表，网站菜单表，访问日志表。 
* 已经实现的功能:
1. CSRF令牌验证:通过对表单使用CSRF令牌验证，有效地防止跨站请求伪造攻击。
2. Session:登录功能中，使用session实现了登陆状态的记忆和自动登录，提供更好的用户体验。
3. 日志记录:使用Django自定义中间件，能够对每个请求进行详细记录并获取主要信息。使用Redis作为缓存数据库和Celery作为任务队列，避免了因日志导致的访问延迟问题。
4. 缓存:对博客主页面和文章详情页进行了缓存处理。用户请求时首先从缓存中获取数据，若缓存未命中，则再向数据库查询。同时设置修改文章或者发布评论时自动删除对应缓存。
5. 网站信息全局定义:根据网站信息表、网站链接表和网站菜单表快速定义网站标题、描述等内容。当网站信息表中存在多行信息时，可以通过level=True字段快速切换不同的标题和描述内容。
6. 高并发支持:利用Redis缓存和Celery任务队列，使博客项目具备了处理大流量访问的能力，保证了系统在高峰期也能正常运行。
7. 评论嵌套:使用`parent_id`和`root_id`字段来实现了评论的嵌套功能。用户可以回复其他人的评论，并形成层级结构，提高了交流与互动效果。
 
# 准备环境配置

* 安装python第三方库
```bash
pip install -r requirements.txt
```

* 安装redis
```
下载地址
https://github.com/tporadowski/redis/releases
```

# 如何运行

1. 修改`djangoblog/setting.py` 修改配置，如下所示:

```python
# mysql配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'djangoblog',
        'USER': 'root',
        'PASSWORD': 'password',
        'HOST': 'host',
        'PORT': 3306,
    }
}

# redis配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # 连接redis超时时间，单位为秒
            "SOCKET_TIMEOUT": 5,  # redis读写操作超时时间，单位为秒
            "CONNECTION_POOL_KWARGS": {"max_connections": 10000}
        }
    }
}

# 任务队列配置
BROKER_URL = "redis://127.0.0.1:6379/1",

celery_result_backend = 'redis://:123456@localhost:6379/1'
```

2. 创建数据库

* mysql数据库中执行:

```sql
CREATE DATABASE djangoblog;
```

* 数据库迁移:

```bash
python manage.py makemigrations
python manage.py migrate
```

* 创建超级用户

```bash
python manage.py createsuperuser
```

3. 开始运行:

* 启动djangoblog

```bash
python manage.py runserver
```

浏览器打开: http://127.0.0.1:8000/
* 启动redis

```bash
redis-server.exe redis.windows.conf
```

* 启动celery任务队列

```bash
celery  -A DjangoBlog worker  -l info -P eventlet
```

--purge:清空队列任务

# 常用命令

* 清空redis

```python
from django_redis import get_redis_connection
redis_conn = get_redis_connection("default")
redis_conn.flushdb()
```

* 清空日志表内容

```mysql
TRUNCATE TABLE access_log;
```

* 查询每秒访问

```mysql
SELECT 
    DATE_FORMAT(request_start_time, '%Y-%m-%d %H:%i:%s') AS time,
    COUNT(*) as `每秒请求数`
FROM access_log
GROUP BY DATE_FORMAT(request_start_time, '%Y-%m-%d %H:%i:%s');
```

* 查询响应状态

```mysql
SELECT 
    status_code AS classification, 
    COUNT(*) AS count, 
    CONCAT(ROUND(COUNT(*) / (SELECT COUNT(*) FROM access_log) * 100, 2), '%') AS percentage
FROM access_log
GROUP BY status_code; 
```

* 查询响应时间

```mysql
SELECT t.`分类`,
       SUM(t.`数量`) AS `数量`,
       ROUND(SUM(t.`数量`) / SUM(total.`总请求数`) * 100, 2) AS `占比(%)`
FROM (
    SELECT '小于1秒的请求数' AS `分类`, 
           SUM(CASE WHEN request_duration < 1000 THEN 1 ELSE 0 END) AS `数量`
    FROM access_log
    UNION ALL
    SELECT '1-3秒的请求数', 
           SUM(CASE WHEN request_duration >= 1000 AND request_duration < 3000 THEN 1 ELSE 0 END)
    FROM access_log
    UNION ALL
    SELECT '3-5秒的请求数', 
           SUM(CASE WHEN request_duration >= 3000 AND request_duration < 5000 THEN 1 ELSE 0 END)
    FROM access_log
    UNION ALL
    SELECT '5-10秒的请求数', 
           SUM(CASE WHEN request_duration >= 5000 AND request_duration <= 10000 THEN 1 ELSE 0 END)
    FROM access_log
    UNION ALL
    SELECT '大于10秒的请求数', 
           SUM(CASE WHEN request_duration > 10000 THEN 1 ELSE 0 END)
    FROM access_log
) t CROSS JOIN (
    SELECT COUNT(*) AS `总请求数` FROM access_log
) total
GROUP BY t.`分类`
ORDER BY FIELD(t.`分类`, '小于1秒的请求数', '1-3秒的请求数', '3-5秒的请求数', '5-10秒的请求数', '大于10秒的请求数');
```
