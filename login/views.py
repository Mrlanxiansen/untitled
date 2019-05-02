from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from . import models
import jiaowu_scrapy

# Create your views here.


def login(request):

    return render(request,'login.html')

def login_check(request):

    if request.method == "POST":
        user = request.POST.get('username',None)
        passwd = request.POST.get('password',None)
        print(user,passwd)
        message = "请填写完所有的字段"
        if user and passwd:

            login_user = jiaowu_scrapy.EduAdmin(user,passwd)
            message = login_user.login()
            print(message['status'])
            print(message["status"])

            # 如果登录成功  保存session
            if message['status'] == 2:
                request.session['user'] = user
                print(request.session['user'])
                return render(request, 'index.html')

            return render(request,'login.html',{"message":message})

        return render(request, 'login.html', {"message": message})


def logout(request):
    if not request.session.get('user', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index")

def register(request):

    return render(request,'register.html')


def register_check(request):
    if request.method == 'POST':
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        email = request.POST.get("email",None)
        school_num = request.POST.get("school_num",None)

        if  username and password and email and school_num :
            login_user = jiaowu_scrapy.EduAdmin(school_num, password)
            message = login_user.login()
            print(message['status'])
            print(message["status"])

            # 如果登录成功  保存session
            if message['status'] == 2:
                new_user = models.person()
                new_user.username = username
                new_user.passwd = password
                new_user.user_email = email
                new_user.user = school_num

                new_user.save()
                print("注册成功")
                return render(request, 'login.html')
            else:

                return render(request, 'register.html', {"message": message})

        else : return render(request, 'register.html', {"message": "信息没有填写完整"})


            #  通过验证开始注册


            # # 发送激活链接,包含所需要的连接  http:127.0.0.1:8848/active
            # # 激活连接中要包含着 人的信息
            # serializer =Serializer(settings.SECRET_KEY,3600)
            # info = {'confirm':new_user.name}
            # token = serializer.dumps(info)
            # token = token.decode()

            # # 发邮件
            # subject = '桂电帮欢迎信息'
            # html_message = '%s,欢迎你成为桂电帮的一员<h1>请点击一下连接来激活您的账户 http://guidianbang.qicp.vip:22154/active/%s ' % (
            #     username, token)
            # sender = settings.EMAIL_FROM
            # reciver = [new_user.email]
            #
            # send_mail(subject,html_message,sender,reciver)
            #
            #


def losspassword():
    pass









