from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'user_name', 'first_name', 'last_name', 'date_joined', 'last_login', 'is_superadmin','is_active')
    list_display_links = ('email','user_name')
    readonly_fields=('date_joined','last_login')
    filter_horizontal=()
    list_filter=()
    fieldsets =()
    ordering=('-date_joined',)

admin.site.register(Account, AccountAdmin)