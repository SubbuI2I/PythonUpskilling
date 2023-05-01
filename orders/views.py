from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm, Order
from datetime import datetime
import json
from .models import Payment

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderId'])
    
    #store payment details to payments model
    payment = Payment(
        user = request.user,
        payment_id = body['transId'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.status = 'Completed'  
    order.save()

    return render(request, 'orders/payments.html')


def place_order(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items is None:
        return redirect('store')
    
    tax = 0 
    total = 0
    grand_total = 0
    for item in cart_items:
        total += item.quantity * item.product.price
    tax = total * 2/100
    grand_total = total + tax
    if request.method == 'POST':
        try:
            form = OrderForm(request.POST)
            if form.is_valid():
                # breakpoint()
                data = Order()
                data.user = request.user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.email = form.cleaned_data['email']
                data.phone = form.cleaned_data['phone']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.city = form.cleaned_data['city']
                data.state = form.cleaned_data['state']
                data.country = form.cleaned_data['country']
                data.zipcode = form.cleaned_data['zipcode']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()
                current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                data.order_number = current_time +'_' + str(data.id)
                data.save()
                order = Order.objects.get(order_number = data.order_number)
                context = {
                    'order':order,
                    'tax': tax,
                    'total':total,
                    'grand_total': grand_total,
                    'cart_items': cart_items
                }
                return render(request, 'orders/payments.html',context)
        except (TypeError, ValueError, Exception) as ex:
            print('invalid form' , ex)
    else:
        return redirect('checkout')
