import logging
import re
import time
from datetime import datetime
from threading import local
from django.core.exceptions import SuspiciousOperation
from django.utils.deprecation import MiddlewareMixin

from Blog.models import Post, AccessLog

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

    def process_request(self, request):
        _thread_locals.request_start_time = time.time()

    def process_view(self, request, view_func, view_args, view_kwargs):
        _thread_locals.view_func = view_func.__name__ if view_func else None
        _thread_locals.view_args = view_args if view_args else None
        _thread_locals.view_kwargs = view_kwargs if view_kwargs else None

    def process_response(self, request, response):

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
            try:
                # 记录访问日志
                access_record = AccessLog(
                    user_id=_thread_locals.user_id,
                    user_name=_thread_locals.username,
                    post_id=_thread_locals.post_id,
                    post_title=_thread_locals.post_title,
                    session_id=request.session.session_key,
                    ip_address=get_client_ip(request),
                    platform_name=request.user_agent.os.family,
                    platform_version=request.user_agent.os.version_string,
                    browser_family=request.user_agent.browser.family,
                    browser_version=request.user_agent.browser.version_string,
                    referer=request.META.get('HTTP_REFERER', ''),
                    request_url=request.build_absolute_uri(),
                    http_method=request.method,
                    body=request.read(),
                    content_type=request.content_type,
                    user_agent_string=str(request.META.get('HTTP_USER_AGENT')),
                    status_code=response.status_code,
                    view_func=_thread_locals.view_func,
                    view_args=_thread_locals.view_args,
                    view_kwargs=_thread_locals.view_kwargs,
                    http_protocol=request.scheme,
                    port_number=request.META.get('SERVER_PORT'),
                    request_start_time=_thread_locals.start_time_str,
                    request_end_time=_thread_locals.end_time_str,
                    request_duration=_thread_locals.duration_ms,
                    response_size=response.get('Content-Length'),
                    http_version=request.META['SERVER_PROTOCOL'],
                )

                # 在数据库中保存访问记录
                access_record.save()

            except SuspiciousOperation as err:
                logger.warning(str(err))
        return response
