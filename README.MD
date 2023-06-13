
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
 终端下执行:
```bash
python manage.py runserver
```

浏览器打开: http://127.0.0.1:8000/
