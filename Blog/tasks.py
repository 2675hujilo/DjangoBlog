import logging

from celery import shared_task

from .models import AccessLog, PostInfo


@shared_task(priority=10, routing_key='low-priority-queue')
def save_access_log(user_id, username, post_id, post_title, session_id, ip_address, platform_name,
                    platform_version, browser_family, browser_version, referer, request_url,
                    http_method, body, content_type, user_agent_string, status_code,
                    view_func=None, view_args=None, view_kwargs=None,
                    http_protocol='http', port_number=80,
                    request_start_time='', request_end_time='', request_duration='',
                    response_size='', http_version=''):
    try:
        # 记录访问日志
        access_record = AccessLog(
            user_id=user_id,
            user_name=username,
            post_id=post_id,
            post_title=post_title,
            session_id=session_id,
            ip_address=ip_address,
            platform_name=platform_name,
            platform_version=platform_version,
            browser_family=browser_family,
            browser_version=browser_version,
            referer=referer,
            request_url=request_url,
            http_method=http_method,
            body=body,
            content_type=content_type,
            user_agent_string=user_agent_string,
            status_code=status_code,
            view_func=view_func,
            view_args=view_args,
            view_kwargs=view_kwargs,
            http_protocol=http_protocol,
            port_number=port_number,
            request_start_time=request_start_time,
            request_end_time=request_end_time,
            request_duration=request_duration,
            response_size=response_size,
            http_version=http_version
        )

        access_record.save()
    except Exception as e:
        logging.warning(str(e))


@shared_task(priority=5, routing_key='low-priority-queue')
def add_post_view(post_title):
    try:
        post_info = PostInfo.objects.get(post_title=post_title)
        post_info.views += 1
        post_info.save()
    except Exception as e:
        logging.warning(str(e))
