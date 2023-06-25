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
    username = models.CharField(max_length=50, verbose_name='用户名')
    reply_to = models.CharField(max_length=50, null=True, blank=True, verbose_name='回复的用户名')
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='评论文章')  # 外键关联到 article 表
    parent_id = models.IntegerField(null=True, blank=True, verbose_name='父评论ID')
    root_id = models.IntegerField(null=True, blank=True, verbose_name='根评论ID')
    content = RichTextUploadingField(config_name='default', verbose_name='评论内容')
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


class NoteForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class AccessLog(models.Model):
    access_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(null=True, blank=True, verbose_name='用户ID')
    user_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='用户名')
    post_id = models.IntegerField(null=True, blank=True, verbose_name='访问文章ID')
    post_title = models.CharField(max_length=255, null=True, blank=True, verbose_name='访问文章标题')
    ip_address = models.CharField(max_length=100, verbose_name='IP地址')
    referer = models.TextField(null=True, blank=True, verbose_name="来源")
    request_url = models.TextField(null=True, blank=True, verbose_name="请求地址")
    http_protocol = models.CharField(max_length=255, null=True, blank=True, verbose_name='协议类型')
    http_method = models.CharField(max_length=10, null=True, blank=True, verbose_name="HTTP请求方法")
    http_version = models.CharField(max_length=255, null=True, blank=True, verbose_name='协议版本')
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
    request_start_time = models.DateTimeField(max_length=50, null=True, blank=True, verbose_name="请求开始时间")
    request_end_time = models.DateTimeField(max_length=50, null=True, blank=True, verbose_name="请求结束时间")
    request_duration = models.IntegerField(null=True, blank=True, verbose_name="请求持续时长(秒)")
    response_size = models.IntegerField(null=True, blank=True, verbose_name='响应数据大小')
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


class SiteInfo(models.Model):
    info_id = models.AutoField(primary_key=True)
    LANG_CHOICES = (
        ('zh', '中文'),
        ('en', 'English'),
    )
    site_title = models.CharField(max_length=200, verbose_name='网站标题')
    site_description = models.TextField(null=True, blank=True, verbose_name='网站描述')
    site_avatar = models.ImageField(null=True, blank=True, verbose_name='网站头像')
    slideshow_images = models.ImageField(null=True, blank=True, verbose_name='首页轮播图')
    language_default = models.CharField(max_length=2, choices=LANG_CHOICES, default='zh', verbose_name='网站默认语言')
    enable_comments = models.BooleanField(default=True, verbose_name='启用评论系统')
    site_menu = models.CharField(max_length=200, null=True, blank=True, verbose_name='菜单')
    site_submenu = models.CharField(max_length=200, null=True, blank=True, verbose_name='子菜单')
    site_links = models.TextField(null=True, blank=True, verbose_name='友情链接')
    class_category = models.CharField(max_length=100, null=True, blank=True, verbose_name='文章分类')
    tag_choice = models.CharField(max_length=128, null=True, blank=True, verbose_name="标签")
    seo_title = models.CharField(max_length=200, null=True, blank=True, verbose_name='页面标题 SEO')
    seo_keywords = models.CharField(max_length=200, null=True, blank=True, verbose_name='meta关键词 SEO')
    seo_description = models.TextField(null=True, blank=True, verbose_name='meta描述 SEO')
    about_me = models.TextField(null=True, blank=True, verbose_name='博主介绍')
    page_footer_notice = models.TextField(null=True, blank=True, verbose_name='页面底部版权声明')
    mobile_friendly_design = models.BooleanField(default=True, null=True, blank=True,
                                                 verbose_name='针对移动设备的响应式设计')
    website_skin_settings = models.ImageField(upload_to='theme', null=True, blank=True,
                                              verbose_name='网站主题/皮肤设置')
    social_media_links_weibo = models.URLField(max_length=200, null=True, blank=True, verbose_name='微博账号链接')
    social_media_links_wechat = models.ImageField(upload_to='wechat_qrcode', null=True, blank=True,
                                                  verbose_name='微信公众号二维码')
    code_highlighting_tool = models.CharField(max_length=30, null=True, blank=True, default="highlight.js",
                                              verbose_name='代码高亮工具')
    comment_system_plugin = models.CharField(max_length=30, null=True, blank=True, default="Disqus",
                                             verbose_name="评论插件")
    article_archive_tree = models.TextField(max_length=30, null=True, blank=True,
                                            default="按照文章发表时间进行归档显示", verbose_name="文章归档")
    lazy_load_tool = models.ImageField(max_length=30, blank=True, null=True, verbose_name='Lazy Load组件')
    backup_database_tool = models.BooleanField(default=True, verbose_name='数据库备份与恢复')
    google_analytics_integration = models.BooleanField(default=True, verbose_name='Google Analytics集成')
    publish_interval_limit = models.PositiveIntegerField(default=10, verbose_name='发布时间间隔限制(分钟)')
    rss_feed_link = models.URLField(max_length=200, blank=True, null=True, verbose_name='RSS feed链接')
    subdomain_binding = models.BooleanField(default=False, null=True, blank=True, verbose_name='二级域名绑定')
    blog_update_email_notification = models.EmailField(null=True, blank=True, verbose_name='博客更新提醒邮件')
    ssl_certificate = models.BooleanField(default=True, null=True, blank=True, verbose_name='SSL证书')
    watermark_setting = models.ImageField(upload_to='watermarks', null=True, blank=True, verbose_name='水印设置')
    site_icp_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='网站备案信息')
    online_customer_service_system = models.URLField(max_length=200, blank=True, null=True,
                                                     verbose_name='在线客服系统链接')
    website_access_statistics = models.TextField(blank=True, null=True, verbose_name='网站访问统计')
    level = models.BooleanField(default=True, verbose_name='启用')

    class Meta:
        db_table = 'site_info'
        verbose_name_plural = '网站信息'


class SiteMenu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='菜单名称')
    url = models.CharField(max_length=10, verbose_name='URL地址')
    menu_root_id = models.IntegerField(blank=True, null=True, verbose_name='根菜单id')
    LEVEL_CHOICES = (
        ('all', '所有人可见'),
        ('guest', '仅游客可见'),
        ('login', '仅已登录用户可见'),
        ('admin', '仅管理员可见'),
    )
    menu_level = models.CharField(max_length=20, default='all', choices=LEVEL_CHOICES, verbose_name='权限等级')
    menu_order = models.IntegerField(default=1, verbose_name='菜单排序')

    class Meta:
        db_table = 'site_menu'
        verbose_name_plural = '网站菜单'


class SiteLink(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_name = models.CharField(max_length=100, verbose_name='链接名称')
    link_url = models.URLField(blank=True, null=True, verbose_name='链接地址')
    link_img_url = models.ImageField(blank=True, null=True, verbose_name='图片地址')
    description = models.TextField(blank=True, null=True, verbose_name='链接描述')
    page_footer_notice = models.TextField(null=True, blank=True, verbose_name='页面底部版权声明')
    LINK_CHOICES = [
        ('user', '用户链接'),
        ('site', '友情链接'),
        ('footer', '底部声明'),

    ]
    link_type = models.TextField(max_length=30, choices=LINK_CHOICES, verbose_name='链接类型')
    link_order = models.IntegerField(default=1, verbose_name='链接顺序')

    class Meta:
        db_table = 'site_link'
        verbose_name_plural = '网站链接'
