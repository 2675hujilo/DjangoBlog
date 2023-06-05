from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(AccessLog)
admin.site.register(Post)