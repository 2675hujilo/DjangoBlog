import logging
import re

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


class AccessLogMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.view_func = None
        self.username = None
        self.user_id = None
        self.post_title = None
        self.post_id = None
        self.session_id = None

    def handle_request(self, request, view_func, view_args, view_kwargs):
        try:
            # 从请求中获取用户信息和文章信息
            if request.user.is_authenticated:
                self.user_id = request.user.user_id
                self.username = request.user.username
            self.session_id = request.session.session_key
            self.post_id = get_post_id(request)
            self.post_title = get_post_title(self.post_id) if self.post_id else None

            # 记录访问日志
            access_record = AccessLog(
                user_id=self.user_id,
                user_name=self.username,
                post_id=self.post_id,
                post_title=self.post_title,
                session_id=self.session_id,
                ip_address=get_client_ip(request),
                platform_name=request.user_agent.os.family,
                platform_version=request.user_agent.os.version_string,
                browser_family=request.user_agent.browser.family,
                browser_version=request.user_agent.browser.version_string,
                referer=request.META.get('HTTP_REFERER', ''),
                request_url=request.build_absolute_uri(),
                http_method=request.method,
                body=request.body,
                content_type=request.content_type,
                user_agent_string=str(request.META.get('HTTP_USER_AGENT')),
                status_code=self.view_func(request, *view_args, **view_kwargs).status_code,
                view_func=view_func.__name__,
                view_args=view_args,
                view_kwargs=view_kwargs,
                http_protocol=request.scheme,
                port_number=request.META.get('SERVER_PORT'),
            )

            # 在数据库中保存访问记录
            access_record.save()

        except SuspiciousOperation as err:
            logger.warning(str(err))

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.view_func = view_func
        self.handle_request(request, view_func, view_args, view_kwargs)
        return None

    def process_exception(self, request, exception):
        self.handle_request(request, self.view_func, (), {})
        raise exception(status=500)
