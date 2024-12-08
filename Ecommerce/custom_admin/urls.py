# urls.py

from django.urls import path
from .views import admin_login, admin_logout
from django.views.generic import TemplateView
from django.urls import path
from .views import (
    # Category views
    category_list,
    category_create,
    category_edit,
    category_view,
    category_delete,

    # Product views
    product_list,
    product_create,
    product_edit,
    product_view,
    product_delete,

    # Customer views
    customer_list,
    customer_create,
    customer_edit,
    customer_delete,
    customer_view,

    # Order views
    order_list,
    order_create,
    order_edit,
    order_view,
    order_delete,
    order_items,

    update_order_status,
    dashboard,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin_login, name='dash_login'),
    path('admin/dashboard', dashboard, name='index'),
    path('logout/', admin_logout, name='admin_logout'), 
    path('category/list',category_list,name="category_list"),
    path('category/create/', category_create, name='category_create'),
    path('category/edit/<int:id>/',category_edit,name='category_edit'),
    path('category/<int:category_id>/view/', category_view, name='category_view'),
    path('category/delete/<int:id>/', category_delete, name='category_delete'),
    path('product/list',product_list,name='product_list'),
    path('product/create',product_create,name="product_create"),
    path('product/edit/<int:id>/',product_edit,name='product_edit'),
    path('product/<int:product_id>/view/', product_view, name='product_view'),
    path('product/delete/<int:id>/',product_delete,name='product_delete'),
    path('customer/list/',customer_list,name='customer_list'),
    path('customer/create/',customer_create,name='customer_create'),
    path('customer/edit/<int:id>/',customer_edit,name='customer_edit'),
    path('customer/<int:customer_id>/view/', customer_view, name='customer_view'),
    path('customer/delete/<int:id>/',customer_delete,name='customer_delete'),
        # URLs for Order views
    path('order/list/', order_list, name='order_list'),
    path('order-items/<int:id>/', order_items, name='order_items'),
    path('order/create/', order_create, name='order_create'),
    path('order/<int:order_id>/view/', order_view, name='order_view'),
    path('order/edit/<int:id>/', order_edit, name='order_edit'),
    path('order/delete/<int:id>/', order_delete, name='order_delete'),
    path('update_order_status/', update_order_status, name='update_order_status'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
