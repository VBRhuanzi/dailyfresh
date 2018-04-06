from django.contrib import admin

# Register your models here.
from django.contrib.admin import ModelAdmin
from django.core.cache import cache

from apps.goods.models import GoodsSKU, GoodsCategory, GoodsSPU, IndexSlideGoods, IndexPromotion

from celery_tasks.tasks import generate_static_index_html



class BaseAdmin(admin.ModelAdmin):
    """当在管理员页面执行修改添加删除数据时，
    1、系统自动调用admin模块里的
    ModelAdmin类的save_model函数进行保存，delete_model函数进行删除，
    定义一个类继承ModelAdmin类重写添加新功能，完成当数据发生改变时，对
    缓存数据进行删除，重新加载保存，完成更新
    2、重新调用generate_static_index_html.delay()触发celery
    异步生成新的静态html文件。"""

    def save_model(self, request, obj, form, change):
        """后台保存对象数据时使用"""

        #一下两种方法一样
        super().save_model(request, obj, form, change)
        # obj表示要保存的对象，调用save(),将对象保存到数据库中
        # obj.save()
        # 调用celery异步生成静态文件方法
        # time.sleep(3)
        generate_static_index_html.delay()

        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        """后台保存对象数据时使用"""
        obj.save()
        # time.sleep(3)
        generate_static_index_html.delay()

        # 修改了数据库数据就需要删除缓存
        cache.delete('index_page_data')


class IndexPromotionBannerAdmin(BaseAdmin):
    """商品活动站点管理，如果有自己的新的逻辑也是写在这里"""
    # list_display = []
    pass

class GoodsCategoryAdmin(BaseAdmin):
    pass

class GoodsSPUAdmin(BaseAdmin):
    pass

class GoodsSKUAdmin(BaseAdmin):
    pass

class IndexSlideGoodsAdmin(BaseAdmin):
    pass

class IndexPromotionsAdmin(BaseAdmin):
    pass


admin.site.register(GoodsCategory,GoodsCategoryAdmin)
admin.site.register(GoodsSPU,GoodsSPUAdmin)
admin.site.register(GoodsSKU,GoodsSKUAdmin)
admin.site.register(IndexSlideGoods,IndexSlideGoodsAdmin)
admin.site.register(IndexPromotion,IndexPromotionsAdmin)