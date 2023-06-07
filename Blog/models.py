from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


# Create your models here.


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True, verbose_name='用户ID')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    email = models.CharField(max_length=100, unique=True, verbose_name='电子邮件')
    password = models.CharField(max_length=100, verbose_name='密码')
    avatar = models.CharField(max_length=255, null=True, blank=True, verbose_name='头像链接')
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
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='评论文章')  # 外键关联到 article 表
    parent_id = models.IntegerField(null=True, blank=True, verbose_name='父评论ID')
    root_id = models.IntegerField(null=True, blank=True, verbose_name='根评论ID')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
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
    platform = models.CharField(max_length=50, null=True, verbose_name='操作系统')
    browser = models.CharField(max_length=255, null=True, verbose_name='浏览器')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'access_log'
        verbose_name_plural = '访问日志'
