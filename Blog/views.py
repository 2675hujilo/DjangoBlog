from django.contrib.auth import authenticate
from django.contrib.auth import login as login_de
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView as LogoutView_de
from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse_lazy
from functools import wraps
from Blog.models import AccessLog, Post, Comment, User, Category


# def log_access(func):
#     @wraps(func)
#     def wrapper(request, *args, **kwargs):
#         # 获取当前登录用户
#
#         user_obj = User.objects.get(user_id=request.user.pk)
#         print("user_obj=",user_obj)
#         user_pk = user_obj if request.user.is_authenticated else None
#         # 获取当前访问的文章id，如果是浏览分类页面，则post_id为None
#         post_id = int(kwargs.get('post_id')) if kwargs.get('post_id') else None
#
#         # 获取访问来源IP地址、平台和浏览器信息等相关信息
#         ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META['REMOTE_ADDR'])
#         platform = request.META.get('HTTP_USER_AGENT', '').split('(')[1].split(';')[0]
#         browser = request.META.get('HTTP_USER_AGENT', '')
#
#         # 创建一条新的访问日志记录
#         access_log = AccessLog(
#             user_id=user_id,
#             post_id=post_id,
#             ip_address=ip_address,
#             platform=platform,
#             browser=browser
#         )
#
#         # 将access_log保存到数据库中，并打印出此次请求的session ID。
#         access_log.save()
#         print(f'Session ID: {request.session.session_key}, '
#               f'User ID: {user_id}, '
#               f'Post ID: {post_id}, '
#               f'IP Address: {ip_address}, '
#               f'Platform: {platform}, '
#               f'Browser: {browser}')
#
#         return func(request, *args, **kwargs)
#
#     return wrapper


# Create your views here.


# def login(request):
#     if request.method == 'POST':
#         username_or_email = request.POST.get('username_or_email')
#         password = request.POST.get('password')
#
#         # 查询数据库，看是否有一条与输入的用户名/邮箱和密码匹配的记录
#         user = User.find_user_by_username_or_email(username_or_email)
#         if user is not None and user["password"] == password:
#             # 匹配成功，将当前时间存为最后登录时间并保存到数据库，并将当前用户 ID 记录到 session 中
#             now = timezone.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # 将当前时间格式化为 yyyy-mm-dd HH:MM:ss.mmm 格式
#             User.objects.filter(pk=user['user_id']).update(last_login_at=now)
#             request.session['user_id'] = user['user_id']
#             return redirect('/index/')
#         else:
#             # 显示错误信息
#             error_msg = "用户名或密码错误！"
#             return render(request, 'blog/login.html', {'error_msg': error_msg})
#
#     else:
#         # GET请求展示登录页面
#         return render(request, 'blog/login.html')
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 使用 Django 的认证系统进行用户验证
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名和密码验证通过，将其登录并跳转到指定链接
            login_de(request, user)
            return redirect('/index/')
        else:
            # 登录失败，提示用户名或密码错误
            error_msg = "用户名或密码错误！"
            return render(request, 'blog/login.html', {'error_msg': error_msg})
    else:
        # GET请求展示登录页面
        return render(request, 'blog/login.html')


# def register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password1 = request.POST.get('password1')
#         password2 = request.POST.get('password2')
#         email = request.POST.get('email')
#
#         # 判断两次输入的密码是否相同
#         if password1 != password2:
#             error_msg = "两次输入的密码不一致！"
#             return render(request, 'blog/register.html', {'error_msg': error_msg})
#
#         # 创建用户并保存到数据库中
#         try:
#             new_user = User(username=username, password=password1, email=email, user_id=None)
#
#             new_user.save()
#             # 注册成功，跳转到登录页面
#             return redirect('/login/')
#         except Exception as e:
#             # 如果创建用户失败，则显示错误信息
#             error_msg = "注册失败：" + str(e)
#             return render(request, 'blog/register.html', {'error_msg': error_msg})
#     else:
#         # 显示注册页面
#         return render(request, 'blog/register.html')
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        print("username=", username, "email=", email, "password=", password1)

        # 检查用户名和邮箱是否已经被注册
        user_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()

        if user_exists:
            error_msg = "用户名已被注册！"
            return render(request, 'blog/register.html', {'error_msg': error_msg})

        if email_exists:
            error_msg = "邮箱已被注册！"
            return render(request, 'blog/register.html', {'error_msg': error_msg})

        # 判断两次输入的密码是否相同
        if password1 != password2:
            error_msg = "两次输入的密码不一致！"
            return render(request, 'blog/register.html', {'error_msg': error_msg})

        # 创建用户并保存到数据库中
        try:
            User.objects.create_user(username=username, email=email, password=password1)

            # 用户创建成功，跳转到登录页面
            success_msg = "注册成功，3秒后跳转到登录页面。"
            return render(request, 'blog/register.html', {'success_msg': success_msg})

        except Exception as e:
            # 如果创建用户失败，则显示错误信息
            error_msg = "注册失败：" + str(e)
            return render(request, 'blog/register.html', {'error_msg': error_msg})
    else:
        # 显示注册页面
        return render(request, 'blog/register.html')


class LogoutView(LogoutView_de):
    template_name = 'blog/index.html'
    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        """
        视图类中的方法，在请求分派给该视图之前执行。
        可以重写此方法进行参数验证、日志记录等处理。
        """
        if request.user.is_authenticated:
            # 清空 session 数据
            request.session.flush()
            return super().dispatch(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy('index'))


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

    return render(request, 'blog/post.html', {'post': post,
                                              'comment_count': comment_count})


def index(request):
    posts = Post.objects.all()
    for post in posts:
        # 部分显示文章内容（前 200 个字符）
        post.content = post.content[:200]
    # 用户已认证
    if request.user.is_authenticated:
        message = '欢迎您，' + str(request.user) + '！'
    # 用户未认证
    else:
        message = '请登录。'

    return render(request, 'blog/index.html', {'posts': posts, 'message': message})


@login_required(login_url='login')
def new_post(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        category_id = request.POST.get('category_id')
        user_pk = request.user.pk
        # 获取分类和用户对象
        category_obj = Category.objects.get(pk=category_id)
        user_obj = User.objects.get(user_id=user_pk)
        post = Post(title=title, content=content, user_id=user_obj)
        post.save()
        # 添加分类到文章中
        post.categories.add(category_obj)

        return redirect('post_detail', pk=post.pk)

    # 如果请求方法不是POST，则返回新的HTTPResponse对象来显示创建文章表单
    context = {'categories': Category.objects.all()}
    return render(request, 'blog/new.html', context)
