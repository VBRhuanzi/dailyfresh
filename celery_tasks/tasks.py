# import os
# import django
# # 设置配置文件
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
# # 初始化django环境
# django.setup()


from celery.app.base import Celery
from django.core.mail import send_mail

from dailyfresh import settings


# 创建celery客户端
# 参数1: 自定义名称
# 参数2: 中间人 使用编号为1的数据库
app = Celery('', broker='redis://127.0.0.1:6379/1')


@app.task
def send_active_mail(username, email, token):
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
              html_message=html_message)     # 使用关键字参数传递html_message


@app.task
def generate_static_index_html():

        pass







