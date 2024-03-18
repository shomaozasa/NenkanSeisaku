from django.db import models
from accounts.models import CustomUser
from django.db.models import Avg
from django.db.models.signals import post_delete

from kadai import settings

# 商品情報

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)  # 商品名
    brand = models.CharField(max_length=255)  # ブランド
    category = models.CharField(max_length=255)  # カテゴリ
    price = models.IntegerField(default=0)  # 価格
    average_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.0)
    product_image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # 商品画像
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)  # 出品者
    description = models.TextField(blank=True, null=True)  # 商品説明


    def __str__(self):
        return self.product_name
    
    def update_average_rating(self):
        average_rating = self.review_set.aggregate(Avg('rating'))['rating__avg']
        self.average_rating = average_rating
        self.save()  

# レビュー情報
    
def update_product_rating(sender, instance, **kwargs):
    product = instance.product_id
    average_rating = product.review_set.aggregate(Avg('rating'))['rating__avg']
    product.average_rating = average_rating
    product.save()

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)  # 商品情報に対する外部キー
    customer_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 顧客情報に対する外部キー
    rating = models.PositiveIntegerField()  # 評価（正の整数）
    comment = models.TextField()  # コメント
    
    def __str__(self):
        return f"Review ID: {self.review_id} (Product: {self.product_id}, Customer: {self.customer_id})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product_id.update_average_rating()
        
post_delete.connect(update_product_rating, sender=Review)

# カート機能

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"CartItem - Cart: {self.cart}, Product: {self.product}, Quantity: {self.quantity}"

# 注文情報

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    total_price = models.IntegerField(default=0)  # 注文の合計金額
    created_at = models.DateTimeField(auto_now_add=True)  # 注文が作成された日時

    def __str__(self):
        return f"Order - ID: {self.order_id}, User: {self.user}, Total Price: {self.total_price}, Created At: {self.created_at}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # 商品の数量

    def __str__(self):
        return f"OrderItem - Order: {self.order}, Product: {self.product}, Quantity: {self.quantity}"