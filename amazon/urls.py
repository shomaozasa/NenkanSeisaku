from django.urls import path
from . import views

app_name = 'amazon'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('product/<int:product_id>', views.ProductDetailView.as_view(), name='product'),
    path('product/register', views.create_product, name='product_register'),
    path('product/delete/<int:product_id>', views.ProductDeleteView.as_view(), name='product_delete'),
    path('address', views.AddressView.as_view(), name='address'),
    path('address/update/<int:pk>/', views.AddressUpdateView.as_view(), name='update_address'),
    path('product_search', views.Product_Search, name='product_search'),
    path('product/<int:product_id>/review', views.ReviewView.as_view(), name='review'),
    path('product/<int:review_id>/review_delete', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('add_to_cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart', views.cart_view, name='cart'),
    path('cart/update/<int:cart_item_id>/', views.CartUpdateView.as_view(), name='cart_update'),
    path('cart/remove/<int:cart_item_id>/', views.CartRemoveView.as_view(), name='cart_remove'),
    path('purchase', views.PurchaseView.as_view(), name='purchase'),
    path('purchase_history', views.PurchaseHistoryView.as_view(), name='purchase_history'),
    path('purchase_successed', views.PurchaseSuccessedView.as_view(), name='purchase_successed'),
]