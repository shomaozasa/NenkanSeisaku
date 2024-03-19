from django.utils import timezone
from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView, CreateView, View,UpdateView
from humanize import intcomma
from .models import Cart, CartItem, Order, OrderItem, Product, Review
from accounts.models import CustomUser
from django.db.models import Q
from .forms import ProductForm, ReviewForm
from django.views.generic.edit import FormView
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import AddressUpdateForm
from .models import CustomUser

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        context['user'] = self.request.user.username
        return context
    
class ProductDetailView(DetailView):
    model = Product
    template_name = 'product.html'  # 商品の詳細ページのテンプレート名
    context_object_name = 'product'  # テンプレートに渡されるコンテキスト変数名
    pk_url_kwarg = 'product_id'  # 商品IDを受け取るためのURLパターン名
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get(self.pk_url_kwarg)
        product = get_object_or_404(Product, pk=product_id)
        if self.request.user.is_authenticated:
            # ユーザーがその商品に対してレビューを行ったかどうかを確認
            user_reviewed = product.review_set.filter(customer_id=self.request.user).exists()
            context['user_reviewed'] = user_reviewed
        cart = Cart.objects.filter(user=self.request.user).first()
        product_in_cart = False
        if cart:
            product_in_cart = cart.cartitem_set.filter(product=product).exists()
        context['product_in_cart'] = product_in_cart
        return context

def create_product(request):
    if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('amazon:index')  # 商品一覧ページにリダイレクト
    else:
        form = ProductForm()
    return render(request, 'product_register.html', {'form': form})

class ProductDeleteView(View):
    def post(self, request, product_id):
        product = Product.objects.get(pk=product_id)
        product.delete()
        return redirect('amazon:index')

class AddressView(TemplateView):
    template_name = 'address.html'
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            user_address = CustomUser.objects.filter(pk=self.request.user.pk).values_list('address', flat=True).first()
            context['address'] = user_address
            context['user'] = self.request.user
        return context
    
class AddressUpdateView(UpdateView):
    model = CustomUser  # 住所を更新するユーザーモデル
    form_class = AddressUpdateForm  # カスタムフォームを指定
    template_name = 'address_update.html'  # 住所更新用のテンプレート
    success_url = reverse_lazy('amazon:address')  # 住所更新後のリダイレクト先URL
    
def Product_Search(request):
    # GETリクエストから検索クエリを取得
    query = request.GET.get('q')
    # 検索クエリがある場合
    if query:
        # 商品名、ブランド、カテゴリ、価格に対して検索を行う
        products = Product.objects.filter(
            Q(product_name__icontains=query) | 
            Q(brand__icontains=query) | 
            Q(category__icontains=query) |
            Q(price__icontains=query) 
        )
    else:
        # 検索クエリがない場合はすべての商品を取得
        products = Product.objects.all()

    if not products:
        message = "検索結果と一致する商品はありませんでした。"
    else:
        message = None
    
    # 検索結果をテンプレートに渡す
    return render(request, 'product_search.html', {'products': products, 'query': query, 'message': message})

class ReviewView(FormView):
    template_name = 'review.html'
    form_class = ReviewForm

    def form_valid(self, form):
        product_id = self.kwargs['product_id']
        product = Product.objects.get(pk=product_id)
        review = form.save(commit=False)
        review.product_id = product
        review.customer_id = self.request.user  # ログインユーザーを取得するための処理が必要
        review.save()
        return redirect('amazon:product', product_id=product_id)
    
class ReviewDeleteView(View):
    def post(self, request, review_id):
        # レビューを取得して削除する
        review = Review.objects.get(pk=review_id)
        review.delete()
        return redirect('amazon:product', product_id=review.product_id.product_id)
    
class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.save()
        return redirect('amazon:product', product_id=product_id)

class RemoveFromCartView(View): #カートから商品を削除(商品ページ)
    def post(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        cart = Cart.objects.get(user=request.user)
        cart.delete()
        return redirect('amazon:product', product_id=product_id)
    
def cart_view(request):
    if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))
    user = request.user
    cart = Cart.objects.filter(user=user).first()
    if cart:
        cart_items = cart.cartitem_set.all()
    else:
        cart_items = []

    return render(request, 'cart.html', {'cart_items': cart_items})

class CartUpdateView(View):
    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.get(id=cart_item_id)
        action = request.POST.get('action')

        if action == 'increase':
            cart_item.quantity += 1
            cart_item.save()
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

        return redirect('amazon:cart')

class CartRemoveView(View): #カートから商品を削除(カートページ)
    def post(self, request, cart_item_id):
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.delete()
        return redirect('amazon:cart')
    
class PurchaseView(View):
    def post(self, request):
        # お届け先
        addresses = CustomUser.objects.filter(id=request.user.id).values_list('address', flat=True)

        # カート内の商品を取得
        cart_items = CartItem.objects.filter(cart__user=request.user)

        # 注文を作成
        order = Order.objects.create(user=request.user, created_at=timezone.now())

        # 注文アイテムを作成し、カート内の商品を注文に追加
        total_price = 0
        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity)
            total_price += cart_item.product.price * cart_item.quantity

        # 注文の合計金額を更新
        order.total_price = total_price
        order.save()

        # カート内の商品を削除
        cart_items.delete()

            # 購入完了後、購入成功ページにリダイレクト
        return redirect('amazon:purchase_successed')
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))
        # カート内の商品を取得
        cart_items = CartItem.objects.filter(cart__user=request.user)

        # 注文の合計金額を計算
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        formatted_total_price = intcomma(total_price)

        # お届け先の情報を取得
        addresses = CustomUser.objects.filter(id=request.user.id).values_list('address', flat=True)

        return render(request, 'purchase.html', {'cart_items': cart_items, 'total_price': formatted_total_price, 'addresses': addresses})
    
class PurchaseHistoryView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))
        # ログイン中のユーザーの購入履歴を取得
        user_orders = OrderItem.objects.filter(order__user=request.user)

        # 商品ごとの合計金額
        for order_item in user_orders:
            order_item.price = order_item.product.price * order_item.quantity
            
        # 合計金額
        total_price = sum(item.product.price * item.quantity for item in user_orders)
        formatted_total_price = intcomma(total_price)

        # 購入履歴をテンプレートに渡す
        return render(request, 'purchase_history.html', {'user_orders': user_orders, 'total_price': formatted_total_price})
    
class PurchaseSuccessedView(TemplateView):
    template_name = 'purchase_successed.html'
