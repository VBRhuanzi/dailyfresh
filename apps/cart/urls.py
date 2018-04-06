from django.conf.urls import url

from apps.cart import views
urlpatterns = [

    url(r'^cart$', views.CartinfoView.as_view(), name='cartinfo'),

    url(r'^add$', views.CartAddView.as_view(), name='cartadd'),

    url(r'^listadd$', views.CartListAddView.as_view(), name='listadd'),

    url(r'^update$', views.CartUpdateView.as_view(), name='update'),

    url(r'^delete', views.CartDeleteView.as_view(), name='delete'),

]