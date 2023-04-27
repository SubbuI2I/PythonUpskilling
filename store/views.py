from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category

# Create your views here.

def store(request, category_slug = None):
    categories = None
    products = None
    count = None
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category = categories)
    else:
        products = Product.objects.all().filter(is_available=True)
    count = products.count()    

    context = {
        'products': products
        ,'product_count': count
        ,'categories': categories
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug = category_slug, slug=product_slug)
    except Exception as ex:
        raise ex
    
    context = {
        'single_product': single_product
    }
    return render(request, 'store/product-detail.html', context)