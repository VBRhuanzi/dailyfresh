from django.db import models


class BaseModel(models.Model):
    """模型类基类"""

    create_time = models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')
    delete = models.SmallIntegerField(default=0, verbose_name='是否删除')

    class Meta(object):
        # 需要指定基类模型类为抽象的,否则迁移生成表时会出错
        abstract = True











