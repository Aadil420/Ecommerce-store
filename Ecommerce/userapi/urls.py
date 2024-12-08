from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import HomeAPIView, SigninAPIView, ShopAPIView, SignupAPIView, SignoutAPIView, CartAPIView, CategoryAPIView,UpdateCartAPIView, RemoveFromCartAPIView, CheckOutAPIView, OrderAPIView, OrderItemsAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('home/', HomeAPIView.as_view(), name='home-api'),
    path('shop/', ShopAPIView.as_view(), name='shop-api'),
    path('signin/', SigninAPIView.as_view(), name='signin-api'),
    path('signup/', SignupAPIView.as_view(), name='signup-api'),
    path('signout/', SignoutAPIView.as_view(), name='signout-api'),
    path('cart/', CartAPIView.as_view(), name='cart-api'),
    path('category/<int:id>/', CategoryAPIView.as_view(), name='category-api'),
    path('update_cart/', UpdateCartAPIView.as_view(), name='update-cart-api'),
    path('remove_from_cart/<int:product_id>/', RemoveFromCartAPIView.as_view(), name='remove-from-cart-api'),
    path('orders/', OrderAPIView.as_view(), name='user_orders_api'),
    path('my-order-items/<int:id>/', OrderItemsAPIView.as_view(), name='user_order_items_api'),
    path('checkout/', CheckOutAPIView.as_view(), name='checkout-api'),
    # path('verify-payment/', VerifyPaymentAPIView.as_view(), name='verify_payment'),
    # path('create_order/', RazorpayOrderAPIView.as_view(), name='create_order'),
    # path('complete_order/', TransactionAPIView.as_view(), name='complete_order'),

]