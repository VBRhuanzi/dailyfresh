from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django.http.response import HttpResponse
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from apps.users.models import Address



class PlaceOrderView(View):

    def post(self, request):
        """进入确认订单界面"""

        # 获取请求参数：sku_ids
        sku_ids = request.POST.getlist('sku_ids')
        # [1, 2]  -> 1,2
        sku_ids_str = ','.join(sku_ids)

        # 校验参数不能为空
        if not sku_ids:
            # 回到购物车界面
            return redirect(reverse('cart:info'))

        # 获取用户地址信息(此处使用最新添加的地址)
        user = request.user
        try:
            address = Address.objects.filter(
                user=user).latest('create_time')
        except:
            address = None

        skus = []           # 订单中所有的商品
        total_count = 0     # 商品总数量
        total_amount = 0    # 商品总金额

        # todo: 查询购物车中的所有的商品
        strict_redis = get_redis_connection()
        # strict_redis = StrictRedis()
        # cart_1 = {1: 2, 2: 2}
        # 字典: 键值,都是bytes类型
        cart_dict = strict_redis.hgetall('cart_%s' % request.user.id)
        # 循环操作每一个订单商品
        for sku_id in sku_ids:
            # 查询一个商品对象
            try:
                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                # 回到购物车界面
                return redirect(reverse('cart:info'))

            # 获取商品数量和小计金额(需要进行数据类型转换)
            sku_count = cart_dict.get(sku_id.encode())  # str -> bytes
            sku_count = int(sku_count)  # bytes -> int
            sku_amount = sku_count * sku.price   # 商品小计金额

            # 新增实例属性,以便在模板界面中显示
            sku.count = sku_count
            sku.sku_amount = sku_amount

            # 添加商品对象到列表中
            skus.append(sku)

            # 累计商品总数量和总金额
            total_count += sku.count
            total_amount += sku_amount

        # 运费(运费模块)
        trans_cost = 10
        # 实付金额
        total_pay = trans_cost + total_amount

        # 定义模板显示的字典数据
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'trans_cost': trans_cost,
            'total_pay': total_pay,
            'address': address,
            'sku_ids_str': sku_ids_str,
        }

        # 响应结果: 返回确认订单html界面
        return render(request, 'place_order.html', context)












# class PlaceOrderView(View):
#
#     def post(self,request):
#
#         # if request.user.is_authenticated():
#         #     return HttpResponse('请先登陆')
#
#         # 获取请求参数：sku_ids
#         sku_ids = request.POST.getlist('sku_ids')
#         print(sku_ids)
#
#         strict_redis = get_redis_connection()
#
#         key = 'cart_%s'%request.user.id
#
#
#         priceall = 0
#         number = 0
#
#         for i in sku_ids:
#
#             cartgoods = GoodsSKU.objects.get(id=int(i))
#             goodss = strict_redis.hgetall(key)
#
#             # 商品对象添加新属性 =  商品对象取得.商品单价 × 商品数量（通过商品id.key值取得value）
#             amunt =  (float(cartgoods.price) * int(goodss[i.encode()]))
#
#             print(type(amunt))
#
#             # 统计总价
#             priceall += amunt
#
#             cartgoods.amunt = amunt
#
#             count = int(goodss[i.encode()])
#
#             number += count
#
#             cartgoods.count = count
#
#
#         data = {
#             "cartgoods":cartgoods,
#             "priceall":priceall,
#             "number":number
#         }
#
#
#         return render(request,'place_order.html',data)