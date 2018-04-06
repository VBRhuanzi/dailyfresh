import re
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired
from redis.client import StrictRedis

from apps.goods.models import GoodsSKU
from apps.users.models import User, Address
from celery_tasks.tasks import send_active_mail
from dailyfresh import settings
from utils.common import LoginRequiredMixin

#进入注册页面
def register(request):
    """进入注册界面"""
    return render(request, 'register.html')

#处理注册
def do_register(request):
    """处理注册"""
    return HttpResponse('进入登录界面')

#注册页面
class RegisterView(View):

    def get(self, request):
        """显示注册界面"""
        return render(request, 'register.html')

    def post(self, request):
        # - 获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        # 同意用户协议,如果勾选了,会传递 'on'
        allow = request.POST.get('allow')

        # - 校验数据合法性
        # 所有的参数都不为空时,all方法才会返回True
        if not all([username, password, password2, email]):
            return render(request, 'register.html', {'errmsg': '参数不能为空'})

        if password != password2:
            return render(request, 'register.html', {'errmsg': '两次输入的密码不一致'})
        #todo
        # if not re.match('^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #     return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 同意用户协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意用户协议'})

        # - 业务：保存用户到数据库表中
        # user = User()
        # user.username = username   # 密码不能明文保存: md5
        # user.password = password
        # user.email = email
        # user.save()
        # 使用django提供的方法新增一个用户 (密码会自动加密)

        # - 不能重复添加用户
        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:  # 数据完整性错误
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # todo: 给用户发送激活邮件
        # 参数1: 密钥
        # 参数2: 过期时间,1小时
        s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60*60)
        # 加密
        token = s.dumps({'confirm': user.id})  # bytes
        token = token.decode()  # bytes -> 字符串类型

        # # 方式一:使用django发送激活邮件
        # self.send_active_mail(username, email, token)
        # 方式二: 使用celery异步发送邮件
        send_active_mail.delay(username, email, token)

        # 修改用户状态为未激活(默认为激活状态)
        user.is_active = False  # 未激活 或者0
        user.save()

        return HttpResponse('进入登录界面')


    def send_active_mail(self, username, email, token):
        """
        发送激活邮件
        :param username: 注册的用户
        :param email:  注册用户的邮箱
        :param token: 对字典 {'confirm':用户id} 加密后的结果
        :return:
        """

        subject = '天天生鲜注册激活'        # 邮件标题
        message = ''                      # 邮件的正文(不带样式)
        from_email = settings.EMAIL_FROM  # 发送者
        recipient_list = [email]          # 接收者, 注意: 需要是一个list
        # 邮件的正文(带有html样式)
        html_message = '<h3>尊敬的%s:</h3>  欢迎注册天天生鲜' \
                       '请点击以下链接激活您的账号:<br/>' \
                       '<a href="http://127.0.0.1:8000/users/active/%s">' \
                       'http://127.0.0.1:8000/users/active/%s</a>' % \
                       (username, token, token)

        # 调用django的send_mail方法发送邮件
        send_mail(subject, message, from_email, recipient_list,
                  html_message=html_message)  # 使用关键字参数传递html_message

#用户激活
class ActiveView(View):

    def get(self, request, token):
        """激活注册账号"""
        # token: 对字典 {'confirm':用户id} 加密后的结果
        try:
            # 对token进行解密
            s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)
            # 解密后得到的是字典
            my_dict = s.loads(token)
            # 获取用户id
            user_id = my_dict.get('confirm')
        except SignatureExpired:  # 激活链接已经过期
            return HttpResponse('链接已经过期')

        # 修改用户状态为已激活
        # user = User.objects.get(id=user_id)
        # user.is_active = True
        # user.save()
        User.objects.filter(id=user_id).update(is_active=True)

        return HttpResponse('激活成功,进入登录界面')

#登陆页面
class LoginView(View):

    def get(self, request):
        """进入登录界面"""
        return render(request, 'login.html')

    def post(self, request):
        """处理登录逻辑"""

        # 获取登录请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  # 是否要保存登录状态

        # 校验参数合法性
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '用户名或密码不能为空'})

        # 使用django提供的认证方法
        # 调用django提供的方法,判断用户名和密码是否正确
        user = authenticate(username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码不正确'})

        # 判断用户名是否有激活
        if not user.is_active:
            return render(request, 'login.html', {'errmsg': '账号未激活'})

        # 调用django的login方法, 记录登录状态(session)
        # 内部会通过session保存登录用户的id
        # _auth_user_id = 1
        login(request, user)

        # 设置session有效期
        if remember == 'on': # 勾选保存用户登录状态
            request.session.set_expiry(None)  # 保存登录状态两周
        else:
            request.session.set_expiry(0)    # 关闭浏览器后,清除登录状态

        # 获取next跳转参数
        next_url = request.GET.get('next', None)
        if next_url is None: # 默认情况,进入首页
            # 响应请求. 进入首页
            return redirect(reverse('goods:index'))
        else:
            # return redirect(reverse(next_url)) # error
            return redirect(next_url)

#用户退出
class LogoutView(View):

    def get(self, request):
        """注销功能:清空用户的session数据(用户id)"""

        # 会清除用户id session数据
        logout(request)

        return redirect(reverse('goods:index'))

#个人信息界面
class UserInfoView(LoginRequiredMixin, View):

    def get(self, request):
        """进入用户个人信息界面"""

        user = request.user  # 登录用户
        # 查询用户最新添加地址
        # 方式一:
        # address = Address.objects.filter(user=user) \
        #     .order_by('-create_time')[0]
        # 方式二: latest: 表示获取最新增的
        try:
            address = user.address_set.all().latest('create_time')
        except Address.DoesNotExist:
            address = None

        # todo: 从Redis数据库中读取用户的商品浏览记录
        # StrictRedis类型
        # strict_redis = get_redis_connection('default')

        strict_redis = get_redis_connection()
        # history_1 = [3, 1, 2]

        key = 'history_%s' % request.user.id
        # redis命令: lrange history_1 0 -1
        # 最多只显示3个商品浏览记录
        # [3, 1, 2]

        sku_ids = strict_redis.lrange(key, 0, 2)
        # 从数据库中查询出用户浏览的商品对象
        skus = GoodsSKU.objects.filter(id__in=sku_ids)

        data = {'which_page': 0, 'address': address, 'skus': skus}
        return render(request, 'user_center_info.html', data)

#订单页面
class UserOrderView(LoginRequiredMixin, View):

    def get(self, request):
        """进入用户订单界面"""

        # if not request.user.is_authenticated():
        #     return HttpResponse('进入登录界面')

        data = {'which_page': 1}
        return render(request, 'user_center_order.html', data)

#用户地址
class UserAddressView(LoginRequiredMixin, View):

    def get(self, request):
        """进入用户地址界面"""

        # 登录用户
        user = request.user
        # 查询用户最新添加地址
        # 方式一:
        # address = Address.objects.filter(user=user) \
        #     .order_by('-create_time')[0]
        # 方式二: latest: 表示获取最新增的
        try:
            address = user.address_set.all().latest('create_time')
        except Address.DoesNotExist:
            address = None

        data = {'which_page': 2, 'address': address}
        return render(request, 'user_center_site.html', data)

    def post(self, request):
        """新增一个用户地址"""
        # 获取请求参数
        receiver = request.POST.get('receiver')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        mobile = request.POST.get('mobile')

        # 判断参数合法性
        if not all([receiver, address, mobile]):
            return render(request, 'user_center_site.html', {'errmsg': '参数不能为空'})

        # 业务: 新增一个地址
        # add = Address()
        # add.receiver_name = receiver
        # add.receiver_mobile = mobile
        # add.save()

        # 登录成功后, django会保存用户对象到request中
        user = request.user
        Address.objects.create(
            receiver_name=receiver,
            receiver_mobile=mobile,
            detail_addr=address,
            zip_code=zip_code,
            user=user
        )
        # 响应请求
        return redirect(reverse('users:address'))






# 需要登录才能访问此视图函数
# 如果没有登录, 会跳转到LOGIN_URL地址
# @login_required
def address(request):
    """进入用户地址界面"""
    data = {'which_page': 2}
    return render(request, 'user_center_site.html', data)












