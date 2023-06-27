
## 运行
修改`djangoblog/setting.py` 修改数据库配置，如下所示：
```python
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
```

### 创建数据库
mysql数据库中执行:
```sql
CREATE DATABASE djangoblog;
```

终端下执行:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户
终端下执行:
```bash
python manage.py createsuperuser
```

### 开始运行：

## 启动djangoblog

http连接:
```bash
python manage.py runserver
```
浏览器打开: http://127.0.0.1:8000/

https连接(自签名证书):
```bash
python manage.py runserver_plus --cert server.crt 127.0.0.1:8000
```
浏览器打开: https://127.0.0.1:8000/

## 启动celery任务队列
```bash
celery  -A DjangoBlog worker  -l info -P eventlet
```

清空redis缓存
```python
from django_redis import get_redis_connection
redis_conn = get_redis_connection("default")
redis_conn.flushdb()
```