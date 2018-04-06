from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from tinymce.models import HTMLField
from utils.models import BaseModel


# AbstractUser: django提供的用户模型类,已经定义了用户相关的一些字段信息
class User(BaseModel, AbstractUser):
    """用户信息模型类"""

    class Meta:
        db_table = 'df_user'


class Address(BaseModel):
    """地址"""

    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    is_default = models.BooleanField(default=False, verbose_name='默认地址')

    user = models.ForeignKey(User, verbose_name="所属用户")

    class Meta:
        db_table = "df_address"


class TestModel(BaseModel):
    """测试用"""

    GENDER_CHOICES = (
        (0, '男'),
        (1, '女'),
    )

    gender = models.SmallIntegerField(default=0, choices=GENDER_CHOICES)
    # 富文本控件
    desc = HTMLField(verbose_name='商品描述', null=True)











