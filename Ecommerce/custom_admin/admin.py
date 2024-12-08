from django.contrib import admin
from .models import Category,Product,Order,Customer,CartItem,Cart
from .models import Order, OrderItem
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
# admin.site.register(CartItem)
# admin.site.register(Cart)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]

admin.site.register(Cart, CartAdmin)

# admin.site.register(Admin_Panel_AuthToken)