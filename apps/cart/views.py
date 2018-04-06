from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection
from redis import StrictRedis

from apps.goods.models import GoodsSKU
from apps.my_apps.aps import extension
from utils.common import LoginRequiredMixin
from apps.my_apps.aps import extension


#购物车页面
class CartinfoView(LoginRequiredMixin,View):

    def get(self, request):

        # 判断用户是否登陆
        # is_authenticated是Django内置的user的方法：用来判断用户是否登陆
        if request.user.is_authenticated():
            pass
            # 接收数据：user_id，sku_id，count

        # strict_redis对象 = get_redis_connection("default")：用于链接redis数据的得到可以获取数据的对象
        strict_redis = get_redis_connection("default")
        # strict_redis = StrictRedis()

        # 获取用户id
        user_id = request.user.id

        # 如果redis中不存在，会返回None
        # 取得hash类型的所有数据（类似多个字典）
        cart_dict = strict_redis.hgetall("cart_%s" % user_id)

        goods_dict = {}

        for i in cart_dict:

            cartgoods = GoodsSKU.objects.get(id=int(i))

            #商品对象添加新属性 =  商品对象取得.商品单价 × 商品数量（通过商品id.key值取得value）
            cartgoods.amunt = "%.2f"%(float(cartgoods.price) * int(cart_dict[i]))

            goods_dict[cartgoods] = int(cart_dict[i])


        goods_total = extension.car_info(request)


        data = {
            'cart_dict':cart_dict,
            'goods_dict':goods_dict,
            'goods_total':goods_total,

        }

        return render(request, 'cart.html', data)


#商品详情页：商品添加到购物车
class CartAddView(LoginRequiredMixin,View):

    def post(self,request):


        # 判断用户是否有登录
        if not request.user.is_authenticated():
            return JsonResponse({'code': 1, 'errmsg': '请先登录'})

        # 获取用户提交的参数
        user_id = request.user.id
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # todo: 判断参数合法性
        if not all([sku_id, count]):
            return JsonResponse({'code': 2, 'errmsg': '请求参数不能为空'})
        # 检验购买数量的合法性
        try:
            count = int(count)
        except:
            return JsonResponse({'code': 3, 'errmsg': '购买数量格式不正确'})
        # 校验商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            return JsonResponse({'code': 4, 'errmsg': '商品不存在'})
        # todo: 业务处理: 添加商品到Redis数据库中
        # 尝试获取redis中商品的购买数量
        # cart_1: {'1':'2', '2':'2'}
        strict_redis = get_redis_connection()
        key = 'cart_%s' % user_id
        # 获取不到会返回None
        val = strict_redis.hget(key, sku_id)
        if val:
            count += int(val)

        # 校验库存是否充足
        if count > sku.stock:
            return JsonResponse({'code': 5, 'errmsg': '库存不足'})

        # 更新商品数量
        strict_redis.hset(key, sku_id, count)

        # todo: 计算购物车中商品的总数量
        #调用子封装包my_apps.返回当前登陆用户购物车商品数量
        cart_count = extension.car_info(request)

        # 响应json数据
        return JsonResponse({'code': 0, 'message': '添加到购物车成功',
                             'cart_count': cart_count})

#ajax 修改购物车商品数量
class CartUpdateView(View):

    def post(self,request):

        #判断用户是否登陆
        if not request.user.is_authenticated():

            return JsonResponse({"code":1,"errmsg":"请先登陆"})

        sku_id = request.POST.get("sku_id")
        count = request.POST.get("count")

        #判断参数是否完整
        if not all([sku_id,count]):
            return JsonResponse({"code":2,"errmsg":"参数不能为空"})

        #获取商品，从而判断商品是否存在
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({"code":3,"errmsg":"商品不存在"})

        #转为整数
        try:
            count = int(count)
        except:
            return JsonResponse({"code":4,"errmsg":"购买数量需为整"})

        #判断库存
        if count > sku.stock:
            return JsonResponse({"code":5,"errmsg":"库存不足"})

        strict_redis = get_redis_connection()

        key = "cart_%s"%request.user.id

        #todo           用户id；商品id；商品数量;
        strict_redis.hset(key,sku_id,count)

        return JsonResponse({"code":0,"errmsg":"商品数量变动"})

#ajax 删除购物车商品
class CartDeleteView(View):

    def post(self,request):

        if not request.user.is_authenticated:

            return JsonResponse({"code":1,"errmsg":"请先登陆"})

        sku_id = request.POST.get("sku_id")

        key = "cart_%s"%request.user.id

        strict_redis = get_redis_connection()

        strict_redis.hdel(key,sku_id)

        # return redirect(reverse('cart:cartinfo'))
        # return redirect("/cart/cart")
        return JsonResponse({"code": 0, "errmsg": "已删除"})

#ajax 商品列表添加商品到购物车
class CartListAddView(View):

    def post(self,request):



        if not request.user.is_authenticated:

            return JsonResponse({"code":1,"errmsg":"请先登陆"})



        sku_id = request.POST.get("sku_id")

        if sku_id=='':

            cart_count = extension.car_info(request)
            return JsonResponse({"cart_count":cart_count})

        strict_redis = get_redis_connection()
        user_id = "cart_%s" % request.user.id
        sku_dict = strict_redis.hgetall(user_id)


        try:
            count = sku_dict.get(sku_id.encode())
        except Exception as e:
            print(e)


        amount = 0

        if not count == None:
            goods = sku_dict[sku_id.encode()]
            print("......",goods)
            amount = int(goods.decode()) + 1

        else:
            amount+=1


        strict_redis.hset(user_id,sku_id,amount)

        cart_count = extension.car_info(request)

        return JsonResponse({"code":0,"errmsg":"添加成功","cart_count":cart_count})























