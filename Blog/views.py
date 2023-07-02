import mimetypes
import os

from django.contrib.auth import authenticate
from django.contrib.auth import login as login_de
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView as LogoutView_de
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.defaults import page_not_found

from Blog.models import Post, Comment, User, Category
from Blog.signals import clear_post


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


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

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


def get_children(request, comment):
    children = Comment.objects.filter(Q(post_id=comment.post_id) & Q(root_id=comment.comment_id) & (
            Q(status="approved") | Q(user_id=request.user.pk))).order_by(
        "created_at")
    for child in children:
        child.children = get_children(request, child)
    return children


def post_detail(request, pk):
    # 获取指定 `pk` 对象的 `Post` 实例，不存在则返回 404 错误
    try:
        # 获取指定 pk 的 Post 实例
        post = Post.objects.get(pk=pk)

        # 如果帖子未公开或不存在
        if post.status != "published":
            raise Http404
            # 更新文章的浏览量
        post.views += 1
        post.save()

        error_msg = None
        comments = None
        page_obj = None
        # 检查用户是否登录，若未登录，则提示请登录；若已登录，则执行下面操作。
        if request.method == "POST":
            if request.user.is_authenticated:
                status = "pending"
                # 管理员默认通过审核
                if request.user.is_superuser:
                    status = "approved"
                content = request.POST.get("content")
                if content:
                    user_id = request.user.pk
                    email = request.POST.get("email")
                    user = User.objects.get(pk=user_id)
                    parent_id = request.POST.get("parent_id")
                    root_id = request.POST.get("root_id")
                    reply_to = request.POST.get("reply_to")
                    old_index = Comment.objects.filter(post_id=post, root_id=None).count()
                    username = user.username
                    # 如果有根评论，则设置reply_to为父评论的username，否则为空
                    if root_id:
                        reply_to = reply_to
                    elif reply_to:
                        reply_to = reply_to
                    else:
                        reply_to = None
                    if parent_id or root_id:
                        new_index = None
                    else:
                        new_index = old_index + 1
                    comment = Comment(
                        user_id=user,
                        username=username,
                        post_id=post,
                        parent_id=parent_id,
                        root_id=root_id,
                        content=content,
                        email=email,
                        status=status,
                        is_top=False,
                        index=new_index,
                        reply_to=reply_to,
                    )
                    comment.save()
                    clear_post(parent_id)
                else:
                    error_msg = "请输入评论内容！"
            else:
                error_msg = "请先登录后再评论！"
        comments = Comment.objects.filter(
            Q(post_id=post.pk) & (Q(status="approved") | Q(user_id=request.user.pk)),
            root_id=None
        ).order_by("created_at")
        if comments:
            for comment in comments:
                comment.children = get_children(request, comment)
            # 创建一个 Paginator 对象，每页显示10个评论，若没有凑成10个则或phans参数指定的数量
            paginator = Paginator(comments, per_page=10, orphans=True)
            # 获取当前请求中page参数的值（即所请求的页数）
            # 如果request.GET中不存在page参数，默认为第一页
            page_num = request.GET.get("page", 1)
            # 调用Paginator对象的get_page()方法获取对应得Page对象
            # 这里传入了page_num作为参数，表示需要返回用户请求的那一页
            page_obj = paginator.get_page(page_num)
        return render(request, "blog/post.html",
                      {"post": post, "comments": comments, "page_obj": page_obj, "error_msg": error_msg})
    except Post.DoesNotExist:
        return HttpResponse(page_not_found(request, None))


def index(request, pk=None):
    cache_ttl = 60 * 15  # 缓存超时时间为15分钟

    if pk:
        cache_key = f"posts_pk_{pk}"
        # 尝试从缓存中读取结果
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            posts = cached_result
        else:
            # 从数据库获取数据
            posts = Post.objects.filter(status="published", categories__category_id=pk).order_by('-updated_at')
            if not posts.exists():  # 检查是否存在符合条件的记录
                return HttpResponse(page_not_found(request, None))  # 返回自定义的 404 页面
            # 写入缓存
            cache.set(cache_key, posts, timeout=cache_ttl)
    else:
        cache_key = "all_posts"
        # 尝试从缓存中读取结果
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            posts = cached_result
        else:
            # 更新数据（如果没有使用缓存，或者原来的缓存已过期）
            posts = Post.objects.filter(status="published").order_by("-updated_at")
            # 写入缓存
            cache.set(cache_key, posts, timeout=cache_ttl)

    for post in posts:
        if '<' in post.content and '>' in post.content:
            start_index = post.content.index('<')
            end_index = post.content.index('>', start_index) + 1
            img_str = post.content[start_index:end_index]
            post.content = post.content.replace(img_str, '', 1)

    paginator = Paginator(posts, per_page=5, orphans=True)
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)

    if request.user.is_authenticated:
        message = '欢迎您，' + str(request.user) + '！'
    else:
        message = '请登录。'

    return render(request, 'blog/index.html', {'message': message, "posts": page_obj})


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


def picture_view(request, path):
    image_path = os.path.join('/media/images/pic/', path)

    # 使用 mimetypes 模块来获取文件的 MIME 类型
    content_type = mimetypes.guess_type(image_path)[0]

    # 如果无法获取 MIME 类型，则默认使用 image/jpeg
    if not content_type:
        content_type = 'image/jpeg'

    return FileResponse(open(image_path, 'rb'), content_type=content_type)


def view_404(request, exception=None):
    return HttpResponse(page_not_found(request, None))
