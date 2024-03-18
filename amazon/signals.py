from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg


from .models import Review, Product

@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, created, **kwargs):
    if created:  # レビューが新規作成された場合のみ処理を実行
        product = instance.product
        reviews = Review.objects.filter(product=product)
        if reviews.exists():  # レビューが存在する場合のみ処理を実行
            average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            product.rating = average_rating
            product.save()

