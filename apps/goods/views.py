from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django_redis import get_redis_connection


from apps.goods.models import GoodsCategory
from apps.goods.models import  IndexSlideGoods
from apps.goods.models import IndexPromotion
from apps.goods.models import  IndexCategoryGoods
from apps.goods.models import GoodsSKU
from apps.my_apps.aps import extension
from apps.users.models import User

#主页数据显示处理
class IndexView(View):

    # def get(self, request):
    #
    #     # 方式一:
    #     # # 从session中获取登录的用户id
    #     # user_id = request.session.get('_auth_user_id')
    #     # # 查询出登录的用户对象
    #     # user = User.objects.get(id=user_id)
    #
    #     # 方式二:
    #     # user = request.user
    #     # print('user=%s' % user.username)
    #
    #     # user = User()
    #     # user.is_authenticated()     # 是否已经登录
    #
    #     return render(request, 'index.html')

    def get(self, request):

        # 获取redis里的缓存数据
        # index_page_data = {...}

        context = cache.get('index_page_data')
        # 是否有缓存
        if context is None:


            # 查询首页中要显示的数据
            # 所有的商品类别
            categories = GoodsCategory.objects.all()
            # 轮播图商品
            slide_goods = IndexSlideGoods.objects.all().order_by('index')
            # 促销活动数据# 只获取2个促销活动
            try:
                promotions = IndexPromotion.objects.all()[0:2]
            except:
                pass

            # 类别商品数据
            # category_skus = IndexCategoryGoods.objects.all()
            # category1
            #     text_skus
            #     imgs_skus
            # category2
            #     text_skus
            #     imgs_skus
            for c in categories:
                # 查询当前类别所有的文字商品和图片商品
                text_skus = IndexCategoryGoods.objects.filter(
                    category=c, display_type=0).order_by('index')
                imgs_skus = IndexCategoryGoods.objects.filter(
                    category=c, display_type=1).order_by('index')
                # 动态地给类别对象,新增属性
                c.text_skus = text_skus
                c.imgs_skus = imgs_skus

            # 定义模板显示的数据
            context = {
                'categories': categories,
                'slide_goods': slide_goods,
                'promotions': promotions
            }
            #       参数1：Key 参数2：value 参数3：有效时间
            cache.set('index_page_data',context,3600)
        else:
            pass

        # 购物车商品数量

        #创建了模块，定义了一个类处理购物车数据
        cart_count = extension.car_info(request)

        context.update(cart_count=cart_count)

        # 响应请求, 显示模板
        return render(request, 'index.html', context)

#单个商品详情
class DetailView(View):

    def get(self,request,sku_id):


        # 查询商品SKU信息
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist:
            # 查询不到商品则跳转到首页
            #考虑到用户自行书写访问不存在数据
            return redirect(reverse('goods:index'))

        # 查询所有商品分类信息
        categories = GoodsCategory.objects.all()

        # 查询最新商品推荐
        #     所有商品(sku)的外键category(类别)对应的某个商品的category(类别)，从而取得一种商品的所有品种
        new_skus = GoodsSKU.objects.filter(category=sku.category).order_by('-create_time')[0:2]

        # 查询其他规格商品
        #某一个商品(sku)的这个商品种类(spu)的所有商品(sku).exclude(排除指定商品的所有商品)
        other_skus = sku.spu.goodssku_set.exclude(id=sku.id)

        # todo 查询购物车信息
        cart_count = 0

        # 如果是登录的用户
        #is_authenticated是Django内置的user的方法：用来判断用户是否登陆
        if request.user.is_authenticated():

            # 获取用户id
            user_id = request.user.id

            # 从redis中获取购物车信息
            # 对象 = get_redis_connection("default")：用于链接redis数据的得到可以获取数据的对象
            redis_conn = get_redis_connection("default")

            # 如果redis中不存在，会返回None
            #取得hash类型的所有数据（类似多个字典）
            cart_dict = redis_conn.hgetall("cart_%s" % user_id)

            for val in cart_dict.values():
                cart_count += int(val)  # 转成int再作累加

            # 保存用户的历史浏览记录
            # history_用户id: [3, 1, 2]

            # 移除现有的商品浏览记录
            key = 'history_%s' % request.user.id
            redis_conn.lrem(key, 0, sku.id)

            # 从左侧添加新的商品浏览记录
            redis_conn.lpush(key, sku.id)

            # 控制历史浏览记录最多只保存3项(包含头尾)
            redis_conn.ltrim(key, 0, 2)

        # 定义模板数据
        context = {
            #所有商品分类信息
            'categories': categories,
            #查询商品SKU信息,一个商品
            'sku': sku,
            #一种商品的所有品种
            'new_skus': new_skus,
            # 购物车商品
            'cart_count': cart_count,
            #一种商品的所有种类,排数此商品
            'other_skus': other_skus,
        }

        # 响应请求,返回html界面
        return render(request, 'detail.html', context)



    def post(self):
        pass

#商品列表详情
class ListView(View):

    def get(self,request,category_id,page_num):


        # 获取sort参数:如果用户不传，就是默认的排序规则
        sort = request.GET.get('sort', 'default')

        # 商品分类信息
        categories = GoodsCategory.objects.all()

        # 新品推荐信息，在GoodsSKU表中，查询特定类别信息，按照时间倒序
        new_skus = GoodsSKU.objects.filter(category=category_id).order_by('-create_time')[0:2]

        # 商品列表信息
        try:
            category = GoodsSKU.objects.get(id=category_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))

        # 按照价格由低到高
        if sort == 'price':

            skus = GoodsSKU.objects.filter(category=category_id).order_by('price')

        # 按照销量由高到低
        elif sort == "hot":

            skus = GoodsSKU.objects.filter(category=category_id).order_by('-sales')

        else:

            skus = GoodsSKU.objects.filter(category=category_id)
            # 无论用户是否传入或者传入其他的排序规则，我在这里都重置成'default'
            sort = 'default'

        # 分页：需要知道从第几页展示
        page_num = int(page_num)

        # 创建分页器：每页两条记录
        paginator = Paginator(skus, 2)

        # 校验page_num：只有知道分页对对象，才能知道page_num是否正确
        try:
            page = paginator.page(page_num)
        except EmptyPage:
            # 如果page_num不正确，默认给用户显示第一页数据
            page = paginator.page(1)

        # 获取页数列表
        page_list = paginator.page_range

        # 购物车
        # 如果是登录的用户
        # 创建了模块，定义了一个类处理购物车数据
        cart_count = extension.car_info(request)

        # 构造上下文
        context = {
            #
            'category': category,
            'categories': categories,
            'page': page,
            'new_skus': new_skus,
            'page_list': page_list,
            'cart_count': cart_count,
            'sort': sort,
        }

        # 渲染模板
        return render(request, 'list.html', context)


    def post(self):
        pass














