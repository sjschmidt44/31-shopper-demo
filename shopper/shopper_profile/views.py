from django.shortcuts import render, redirect, get_object_or_404
from shopper_products.models import Product, Photo
from .models import ShopperProfile


def profile_view(request, username=None):
    owner = False

    if not username:
        username = request.user.get_username()
        owner = True
        if username == '':
            return redirect('home')

    profile = get_object_or_404(ShopperProfile, user__username=username)
    products = Product.objects.filter(user__username=username)
    photos = Photo.objects.filter(product__user__username=username)

    if not owner:
        photos = Photo.objects.filter(published='PUBLIC')
        products = Product.objects.filter(published='PUBLIC')

    context = {
        'profile': profile,
        'products': products,
        'photos': photos
    }

    return render(request, 'shopper_profile/profile.html', context)
