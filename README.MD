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

1. 修改`djangoblog/setting.py` 修改配置，如下所示：

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

3. 开始运行：

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
