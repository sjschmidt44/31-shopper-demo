from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Photo
from django.conf import settings


def store_view(request):
    if not request.user.is_authenticated:
        return redirect('home')

    context = {
        'products': Product.objects.filter(published='PUBLIC'),
        'cover': settings.STATIC_URL + 'default_cover.thumbnail',
    }

    return render(request, 'store/store.html', context)


def product_detail_view(request, pk=None):
    if not request.user.is_authenticated:
        return redirect('home')

    context = {
        'product': get_object_or_404(Product, id=pk),
        'photos': Photo.objects.filter(product__id=pk),
    }

    return render(request, 'store/product_detail.html', context)
