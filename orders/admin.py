from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display=['first_name', 'last_name','order_number','order_total','phone','payment','status']

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)