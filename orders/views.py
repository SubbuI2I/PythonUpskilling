from django.shortcuts import render,redirect
from carts.models import CartItem
from .forms import OrderForm, Order
from datetime import datetime
import json
from .models import Payment, OrderProduct
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.

def payments(request):
    body = json.loads(request.body)
    # print(body)
    order = Order.objects.get(order_number=body['orderId'])
    
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

    #Move the cart items to order product
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderProduct = OrderProduct()
        orderProduct.user = request.user
        orderProduct.payment = payment
        orderProduct.order = order
        # orderProduct.user.id = request.user.id
        orderProduct.product = item.product
        orderProduct.quantity = item.quantity
        orderProduct.product_price = item.product.price
        orderProduct.is_ordered = True
        orderProduct.save()
        cart_item = CartItem.objects.get(id=item.id)
        product_variations = cart_item.variations.all()
        orderProduct.variations.set(product_variations)
        orderProduct.save()

        #reduce stock count based on order products
        product = Product.objects.get(id=item.product.id)        
        product.stock -= item.quantity
        product.save()
    
    CartItem.objects.filter(user=request.user).delete()

    #send order received mail to customer
    mail_subject = 'Thank you for ordering !'
    message = render_to_string('orders/order-received-email.html',{
        'user': request.user,
        'order': order
    })
    to_mail = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_mail])
    # send_email.send()
    data = {
        'order_number': order.order_number,
        'transId': payment.payment_id,
        'status': payment.status
    }
    return JsonResponse(data)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transId = request.GET.get('transId')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transId)
        subtotal = 0
        for item in ordered_products:
            subtotal += item.quantity * item.product_price
        tax = 2*subtotal/100
        # grand_total = subtotal + tax

        context = {
            'order' : order,
            'ordered_products': ordered_products,
            'transId': transId,
            'payment': payment,
            'subtotal': subtotal,
            'tax': tax,
            # 'grand_total': grand_total
        }
        return render(request, 'orders/order-complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('store')

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
            else:
                print('invalid form', form )                
        except (TypeError, ValueError, Exception) as ex:
            print('invalid form' , ex)
    else:
        return redirect('checkout')
