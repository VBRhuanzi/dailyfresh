from django.conf.urls import url

from apps.goods import views

urlpatterns = [
    #进入首页
    url(r'^index$', views.IndexView.as_view(), name='index'),

    #商品详情页面
    url(r'^detail/(?P<sku_id>\d+)$', views.DetailView.as_view(), name='detail'),
    #商品列表详情
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)$',views.ListView.as_view(), name='list'),

    # url(r'^car_add/(?P<goods_id>\d+)/(?P<number>\d+)$',views.CarAddView.as_view(), name='car_add'),


]