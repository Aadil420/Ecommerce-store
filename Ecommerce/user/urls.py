from django.urls import path
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import Home,Signin,signout,signup,CartView,category_view,ShopView,update_cart,remove_from_cart,CheckOut,OrderView,order_items
# from user.middlewares.auth import auth_middleware



urlpatterns = [
    path('', Home.as_view(), name='homepage'),
    path('signin/', Signin.as_view(), name="signin"),
    path('signup/', signup.as_view(), name='signup'),
    path('signout/', signout, name='signout' ),
    path('shop/', ShopView.as_view(), name='shop' ),
    path('cart/', CartView.as_view(), name='cart'),
    path('category/<int:id>/', category_view, name='category'),
     path('update_cart/', update_cart, name='update_cart'),
     path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
     path('check-out/', CheckOut.as_view(), name='checkout'),
     path('orders', OrderView.as_view(), name='user_orders' ),
     path('my-order-items/<int:id>/', order_items, name='user_order_items'),
    # path('process_payment/', process_payment, name='process_payment'),
    # path('order_success/', order_success, name='order_success'),
    # path('orders/', auth_middleware(OrderView.as_view()), name='orders' )
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
