from django.utils import timezone
from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from Blog.models import AccessLog, Post, Comment, User


# Create your views here.


def login(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # 查询数据库，看是否有一条与输入的用户名/邮箱和密码匹配的记录
        user = User.find_user_by_username_or_email(username_or_email)
        if user is not None and user["password"] == password:
            # 匹配成功，将当前时间存为最后登录时间并保存到数据库，并将当前用户 ID 记录到 session 中
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 将当前时间格式化为 yyyy-mm-dd HH:MM:ss.mmm 格式
            User.objects.filter(pk=user['user_id']).update(last_login_at=now)
            request.session['user_id'] = user['user_id']
            return redirect('/index/')
        else:
            # 显示错误信息
            error_msg = "用户名或密码错误！"
            return render(request, 'blog/login.html', {'error_msg': error_msg})

    else:
        # GET请求展示登录页面
        return render(request, 'blog/login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        # 判断两次输入的密码是否相同
        if password1 != password2:
            error_msg = "两次输入的密码不一致！"
            return render(request, 'blog/register.html', {'error_msg': error_msg})

        # 创建用户并保存到数据库中
        try:
            new_user = User(username=username, password=password1, email=email, user_id=None)

            new_user.save()
            # 注册成功，跳转到登录页面
            return redirect('/login/')
        except Exception as e:
            # 如果创建用户失败，则显示错误信息
            error_msg = "注册失败：" + str(e)
            return render(request, 'blog/register.html', {'error_msg': error_msg})
    else:
        # 显示注册页面
        return render(request, 'blog/register.html')


@login_required
def log_access(request, post_id=None):
    # 获取当前登录用户
    user_id = request.user.id
    # 获取当前访问的文章id，如果是浏览分类页面，则post_id为None
    post_id = int(post_id) if post_id else None
    # 获取访问来源IP地址、平台和浏览器信息等相关信息
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
    platform = request.META.get('HTTP_USER_AGENT', '').split('(')[1].split(';')[0]
    browser = request.META.get('HTTP_USER_AGENT', '')

    # 创建一条新的访问日志记录
    access_log = AccessLog(
        user_id=user_id,
        post_id=post_id,
        ip_address=ip_address,
        platform=platform,
        browser=browser
    )

    # 将access_log保存到数据库中，并打印出此次请求的session ID。
    access_log.save()
    print(f'Session ID: {request.session.session_key}, '
          f'User ID: {user_id}, '
          f'Post ID: {post_id}, '
          f'IP Address: {ip_address}, '
          f'Platform: {platform}, '
          f'Browser: {browser}')

    return HttpResponse('Access log saved.')


def post_list(request):
    # 获取所有文章实例（包括浏览量 views、点赞数 likes 和点踩数 dislikes）
    posts = Post.objects.all().annotate(comment_count=Count('comment'))

    for post in posts:
        # 部分显示文章内容（前 200 个字符）
        post.content = post.content[:200]

    return render(request, 'blog/index.html', {'posts': posts})


def post_detail(request, pk):
    # 获取指定 `pk` 对象的 `Post` 实例，不存在则返回 404 错误
    post = get_object_or_404(Post, pk=pk)

    # 更新文章的浏览量
    post.views += 1
    post.save()

    # 获取该文章的所有评论实例，并统计数量
    comments = Comment.objects.filter(post_id=post.pk)
    comment_count = comments.count() if comments.exists() else 0

    # 更新模板上下文，部分显示内容长度为前 200 字符
    post.content = post.content[:200]

    return render(request, 'blog/post_detail.html', {'post': post,
                                                     'comment_count': comment_count})


def index(request):
    # 获取所有文章实例
    posts = Post.objects.all()
    for post in posts:
        # 部分显示文章内容（前 200 个字符）
        post.content = post.content[:200]

    return render(request, 'blog/index.html', {'posts': posts})
