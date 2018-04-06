from urllib import request

from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU


class My_extension(object):

    def car_info(self,request):

        if request.user.is_authenticated():

            user_id = request.user.id

            key = 'cart_%s'%user_id

            radis_conn = get_redis_connection('default')

            key_dict = radis_conn.hgetall(key)

            cart_count = 0

            for i in key_dict.values():
                cart_count += int(i)

            return cart_count
        else:
            return 0

extension = My_extension()

class My_user_cartinfo(object):

    def cartinfo(self,request):

        if request.user.is_authenticated:

            user_id = request.user.id

            strict_redis = get_redis_connection("default")

            # 如果redis中不存在，会返回None
            # 取得hash类型的所有数据（类似多个字典）
            cart_dict = strict_redis.hgetall("cart_%s" % user_id)

            cart_info_dict = {}

            for i in cart_dict:
                cartgoods = GoodsSKU.objects.get(id=int(i))
                # 商品对象添加新属性 =  商品对象取得.商品单价 × 商品数量（通过商品id.key值取得value）
                cartgoods.amunt = "%.2f" % (float(cartgoods.price) * int(cart_dict[i]))

                cart_info_dict[cartgoods] = int(cart_dict[i])

            return cart_info_dict
        else:
            return None
