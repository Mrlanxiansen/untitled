"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,re_path

from index import views as index_views
from login import views as login_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # 主页
    path('index/',index_views.index,name='index'),

    # 登录有关的页面
    re_path(r'login/$', login_views.login,),
    re_path(r'login_check/$', login_views.login_check,name='login_check'),
    re_path(r'logout/$',login_views.logout),

    path('register/',login_views.register),
    re_path(r'register_check/$',login_views.register_check),

]
