from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == 'POST':
        # color = request.POST["color"]
        # size = request.POST["size"]
        # print(request.method)
        for item in request.POST:
            if not item == 'csrfmiddlewaretoken':
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.filter(product=product, variation_category__iexact=key, variation_value__iexact=value).first()
                    # print(variation)
                    product_variations.append(variation)
                except Variation.DoesNotExist:
                    variation = None
            else:
                pass
    if not current_user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get cart id using _cart_id function from cookies session in browser
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id= _cart_id(request)
            )
            cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart)
        cart_items = CartItem.objects.filter(product=product, cart=cart)
    else:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user)
        cart_items = CartItem.objects.filter(product=product, user=current_user)

    if is_cart_item_exists:
        # if len(product_variations) > 0:
        #     cart_item.variations.clear()
        #     for item in product_variations:
        #         cart_item.variations.add(item)            
        # cart_item.quantity += 1

        ex_var_list = []
        id=[]
        for item in cart_items:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            id.append(item.id)
        
        if product_variations in ex_var_list:
            index = ex_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(id= item_id) # product=product, id=item_id
            item.quantity += 1
            item.save()
        else:
            if current_user.is_authenticated: 
                cart_item = CartItem.objects.create(product=product, user=current_user)
            else:
                cart_item = CartItem.objects.create(product=product, cart=cart)
            if len(product_variations) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variations)
            cart_item.save()
    else:
        if current_user.is_authenticated: 
            cart_item = CartItem.objects.create(
                product = product, 
                user = current_user,
                quantity = 1
            )
        else:
            cart_item = CartItem.objects.create(
                product = product, 
                cart = cart,
                quantity = 1
            )
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    # output = f'<li>{cart_item.product}</li>'
    # return HttpResponse(cart_item.product)
    return redirect('cart')

def remove_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product = product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user)        
    else: 
        cart = Cart.objects.get(cart_id=_cart_id(request))    
        cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items = None):
    tax = None
    grand_total = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2*total)/100
        grand_total = total + tax 
    except ObjectDoesNotExist:
        pass #just ignore only object does not exist

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }
    
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items = None):
    tax = None
    grand_total = None
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
           cart = Cart.objects.get(cart_id=_cart_id(request))
           cart_items = CartItem.objects.filter(cart = cart, is_active=True)
        for item in cart_items:
            total += item.product.price * item.quantity
            quantity += item.quantity
        tax = (2*total)/100
        grand_total = total + tax 
    except ObjectDoesNotExist:
        pass #just ignore only object does not exist

    context = {
        'total' : total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }    
    return render(request, 'store/checkout.html', context)