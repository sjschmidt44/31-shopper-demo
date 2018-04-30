from django.urls import path
from .views import store_view, product_detail_view


urlpatterns = [
    path('', store_view, name='store'),
    path('products/<int:pk>', product_detail_view, name='product_detail'),
]
