"""DjangoBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from django.views.static import serve

from Blog import views
from Blog.views import LogoutView, picture_view
from django.conf.urls.static import static
from django.conf import settings

from DjangoBlog.settings import MEDIA_ROOT

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', RedirectView.as_view(url='index/')),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('new/', views.new_post, name='new_post'),
    re_path(r'^media/uploads/(?P<path>.*)/$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/images/pic/(?P<path>.*)/$', picture_view),
    re_path(r'^static/images/pic/(?P<path>.*)/$', picture_view),
    re_path(r'^static/images/(?P<path>.*)/$', picture_view),
    re_path(r'ckeditor/', include('ckeditor_uploader.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
