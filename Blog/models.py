from django.db import models

# Create your models here.

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    nickname = models.CharField(max_length=50, null=False, blank=False)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('secret', 'Secret'),
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default='secret',
        null=True
    )
    birthday = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)
    social_links = models.TextField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_login_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user'

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
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="children"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category'


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    status_choice = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ]
    status = models.CharField(choices=status_choice, max_length=9)
    meta_keywords = models.TextField(null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='posts')
    class Meta:
        db_table = 'post'


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)  # 外键关联到 user 表
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)  # 外键关联到 article 表
    parent_id = models.IntegerField(null=True, blank=True)
    root_id = models.IntegerField(null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    status_choice = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending')
    ]
    status = models.CharField(choices=status_choice, max_length=9)
    is_top = models.BooleanField()
    email = models.EmailField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comment'


class AccessLog(models.Model):
    access_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post_id = models.IntegerField(null=True)
    ip_address = models.CharField(max_length=100)
    platform = models.CharField(max_length=50, null=True)
    browser = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_log'
