import logging
import re
import time
from datetime import datetime
from threading import local

from django.core.exceptions import SuspiciousOperation
from django.utils.deprecation import MiddlewareMixin

from Blog.models import Post
from Blog.tasks import save_access_log

logger = logging.getLogger(__name__)


def get_post_title(post_id):
    post_title = None
    if post_id:
        post_title = Post.objects.get(post_id=post_id).title
    return post_title if post_title else None


def get_post_id(request):
    # 正则表达式匹配出 URL 中的文章编号
    post_id_str = re.search(r'post/(\d+)/', request.path)
    if post_id_str:
        post_id = int(post_id_str.group(1))
    else:
        post_id = None

    return post_id


def is_valid_ip_address(ip_address):
    pattern = r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
    try:
        # 使用正则表达式匹配IP地址
        if re.match(pattern, ip_address):
            return True
        else:
            return False
    except TypeError:  # 处理非字符串类型的输入
        return False


def get_client_ip(request):
    # 获取客户端 IP 地址
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_addresses = x_forwarded_for.split(',')
        ip_address = ip_addresses[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR', '')

    # 如果IP地址不合法
    if not is_valid_ip_address(ip_address):
        suspicious_message = f"Suspicious IP address detected: {ip_address}"
        logger.warning(suspicious_message)
        raise SuspiciousOperation(suspicious_message)

    return ip_address


_thread_locals = local()  # 线程本地存储


class AccessLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)

    @staticmethod
    def process_request(request):
        _thread_locals.request_start_time = time.time()

    @staticmethod
    def process_view(request, view_func, view_args, view_kwargs):
        _thread_locals.view_func = view_func.__name__ if view_func else None
        _thread_locals.view_args = view_args if view_args else None
        _thread_locals.view_kwargs = view_kwargs if view_kwargs else None

    @staticmethod
    def process_response(request, response):

        if hasattr(_thread_locals, 'request_start_time'):
            request_end_time = time.time()
            request_start_time = getattr(_thread_locals, 'request_start_time', 0)

            _thread_locals.start_time_str = datetime.fromtimestamp(request_start_time).strftime("%Y-%m-%d %H:%M:%S.%f")
            _thread_locals.end_time_str = datetime.fromtimestamp(request_end_time).strftime("%Y-%m-%d %H:%M:%S.%f")
            _thread_locals.duration_ms = int((request_end_time - request_start_time) * 1000)
            _thread_locals.user_id = None
            _thread_locals.username = None
            if request.user:
                if request.user.is_authenticated:
                    _thread_locals.user_id = request.user.user_id
                    _thread_locals.username = request.user.username

            _thread_locals.post_id = get_post_id(request)
            _thread_locals.post_title = get_post_title(_thread_locals.post_id)
            save_access_log.delay(_thread_locals.user_id,
                                  _thread_locals.username,
                                  _thread_locals.post_id,
                                  _thread_locals.post_title,
                                  request.session.session_key,
                                  get_client_ip(request),
                                  request.user_agent.os.family,
                                  request.user_agent.os.version_string,
                                  request.user_agent.browser.family,
                                  request.user_agent.browser.version_string,
                                  request.META.get('HTTP_REFERER', ''),
                                  request.build_absolute_uri(),
                                  request.method,
                                  request.read(),
                                  request.content_type,
                                  str(request.META.get('HTTP_USER_AGENT')),
                                  response.status_code,
                                  getattr(_thread_locals, 'view_func', None),
                                  getattr(_thread_locals, 'view_args', None),
                                  getattr(_thread_locals, 'view_kwargs', None),
                                  request.scheme,
                                  request.META.get('SERVER_PORT'),
                                  _thread_locals.start_time_str,
                                  _thread_locals.end_time_str,
                                  _thread_locals.duration_ms,
                                  response.get('Content-Length'),
                                  request.META['SERVER_PROTOCOL'],
                                  )
        return response
