from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(AccessLog)
admin.site.register(Post)
admin.site.register(SiteInfo)
admin.site.register(SiteMenu)
admin.site.register(SiteLink)
admin.site.register(PostInfo)
