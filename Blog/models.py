from ckeditor_uploader.fields import RichTextUploadingField
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from mptt.models import MPTTModel
from user_agents import parse


# Create your models here.


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    email = models.CharField(max_length=100, unique=True, verbose_name='电子邮件')
    password = models.CharField(max_length=100, verbose_name='密码')
    avatar = models.ImageField(max_length=255, null=True, blank=True, verbose_name='头像链接')
    nickname = models.CharField(max_length=50, null=False, blank=False, verbose_name='昵称')
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
        ('secret', '保密'),
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='secret',
        null=True,
        verbose_name='性别'
    )
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='位置')
    introduction = models.TextField(null=True, blank=True, verbose_name='个人介绍')
    website = models.CharField(max_length=255, null=True, blank=True, verbose_name='个人网站')
    social_links = models.TextField(null=True, blank=True, verbose_name='社交链接')
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    last_login_at = models.DateTimeField(auto_now=True, verbose_name='最后登录时间')

    class Meta:
        db_table = 'user'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

    @classmethod
    def find_user_by_username_or_email(cls, username_or_email):
        try:
            user = cls.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
            return {"user_id": user.user_id, "password": user.password, "last_login_at": user.last_login_at}
        except cls.DoesNotExist:
            return None


class Category(models.Model):
    category_id = models.AutoField(primary_key=True, verbose_name='分类ID')
    name = models.CharField(max_length=255, verbose_name='分类名')
    description = models.TextField(null=True, blank=True, verbose_name='分类介绍')
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="children", verbose_name='父级分类'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'category'
        verbose_name_plural = '分类'


class Post(models.Model):
    post_id = models.AutoField(primary_key=True, verbose_name='文章ID')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户ID')
    title = models.CharField(max_length=255, verbose_name='文章标题')
    content = RichTextUploadingField(verbose_name='正文内容', config_name='default')
    image_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='配图链接')
    published_at = models.DateTimeField(null=True, blank=True, auto_now_add=True, verbose_name='发布时间')
    views = models.IntegerField(default=0, verbose_name='阅读量')
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    dislikes = models.IntegerField(default=0, verbose_name='踩数')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    status_choice = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档')
    ]
    status = models.CharField(choices=status_choice, max_length=9, default="published", verbose_name='文章状态')
    meta_keywords = models.TextField(null=True, blank=True, verbose_name='SEO关键词')
    meta_description = models.TextField(null=True, blank=True, verbose_name='SEO描述')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    categories = models.ManyToManyField(Category, related_name='posts', verbose_name='分类')

    class Meta:
        db_table = 'post'
        verbose_name_plural = '文章'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')  # 外键关联到 user 表
    username = models.CharField(max_length=50,verbose_name='用户名')
    reply_to = models.CharField(max_length=50,null=True, blank=True, verbose_name='回复的用户名')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='评论文章')  # 外键关联到 article 表
    parent_id = models.IntegerField(null=True, blank=True, verbose_name='父评论ID')
    root_id = models.IntegerField(null=True, blank=True, verbose_name='根评论ID')
    content = RichTextUploadingField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    index = models.IntegerField(null=True, blank=True, verbose_name="楼层")
    likes = models.IntegerField(default=0, verbose_name='点赞数')
    dislikes = models.IntegerField(default=0, verbose_name='踩数')
    status_choice = [
        ('approved', '已审核'),
        ('rejected', '已拒绝'),
        ('pending', '待审核')
    ]
    status = models.CharField(choices=status_choice, max_length=9, verbose_name='状态', default="pending")
    is_top = models.BooleanField(verbose_name='是否置顶')
    email = models.EmailField(null=True, blank=True, verbose_name='电子邮件')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'comment'
        verbose_name_plural = '评论'


class AccessLog(models.Model):
    access_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True, verbose_name='用户ID')
    user_name = models.CharField(max_length=50, verbose_name='用户名', null=True, blank=True)
    post_id = models.IntegerField(null=True, blank=True, verbose_name='访问文章ID')
    post_title = models.CharField(max_length=255, null=True, blank=True, verbose_name='访问文章标题')
    ip_address = models.CharField(max_length=100, verbose_name='IP地址')
    referer = models.TextField(null=True, blank=True, verbose_name="来源")
    request_url = models.TextField(null=True, blank=True, verbose_name="请求地址")
    http_protocol = models.CharField(max_length=255, null=True, blank=True, verbose_name='http协议')
    http_method = models.CharField(max_length=10, null=True, blank=True, verbose_name="HTTP 请求方法")
    user_agent_string = models.TextField(null=True, blank=True, verbose_name="用户代理字符串")
    body = models.TextField(null=True, blank=True, verbose_name="请求体")
    content_type = models.CharField(max_length=255, verbose_name='请求类型', null=True, blank=True)
    view_func = models.CharField(max_length=255, verbose_name='视图函数', null=True, blank=True)
    view_args = models.TextField(max_length=255, verbose_name='位置参数', null=True, blank=True)
    view_kwargs = models.TextField(max_length=255, verbose_name='关键字参数', null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True, verbose_name='响应代码')
    session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='会话ID')
    port_number = models.IntegerField(null=True, blank=True, verbose_name='端口')
    platform_name = models.CharField(max_length=50, null=True, verbose_name='操作系统名称')
    platform_version = models.CharField(max_length=50, null=True, verbose_name='操作系统版本')
    browser_family = models.CharField(max_length=50, null=True, verbose_name='浏览器品牌')
    browser_version = models.CharField(max_length=50, null=True, verbose_name='浏览器版本')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'access_log'
        verbose_name_plural = '访问日志'

    @property
    def user_agent(self):
        return parse(self.user_agent_string)

    @property
    def device_type(self):
        return str(self.user_agent.device)

    @property
    def browser_name(self):
        return str(self.user_agent.browser)

    @property
    def os(self):
        return str(self.user_agent.os)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
