# 设置环境变量
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "DjangoBlog.settings")

# 实例化celery
app = Celery("Blog")

# 使用django的配置文件进行配置
app.config_from_object('django.conf.settings')