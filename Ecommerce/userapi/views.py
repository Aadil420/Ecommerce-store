from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from custom_admin.models import Product, Category, Customer, Product, Order, OrderItem, Cart, CartItem
from .serializers import ProductSerializer, CategorySerializer, CustomerSerializer, OrderSerializer, ProductSerializer, OrderItemSerializer, CartItemSerializer
from .utils import get_tokens_for_user 
import re
from django.contrib.auth import logout
from django.conf import settings
import razorpay
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication

class HomeAPIView(APIView):
    def get_cart(self, request):
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            cart, created = Cart.objects.get_or_create(customer=customer)
        else:
            cart = None
        return cart

    def get(self, request):
        # Fetch all products
        products = Product.objects.filter(deleted_at__isnull=True)
        product_serializer = ProductSerializer(products, many=True)

        # Fetch all categories
        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)
        
        # Fetch cart items for the authenticated user
        cart = self.get_cart(request)
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            cart_item_serializer = CartItemSerializer(cart_items, many=True)
            cart_data = cart_item_serializer.data
        else:
            cart_data = []

        return Response({
            'categories': category_serializer.data,
            'products': product_serializer.data,
            'cart_items': cart_data
        }, status=status.HTTP_200_OK)
    
class SigninAPIView(APIView):
    return_url = None

    def get(self, request):
        cart = request.session.get('cart', {})
        request.session['cart'] = cart

        SigninAPIView.return_url = request.GET.get('return_url')
        return Response({'message': 'GET request received', 'return_url': SigninAPIView.return_url}, status=status.HTTP_200_OK)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None

        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id
                tokens = get_tokens_for_user(customer)

                response_data = {
                    'refresh': tokens['refresh'],
                    'access': tokens['access'],
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'phone': customer.phone,
                    'email': customer.email,
                }

                if SigninAPIView.return_url:
                    response_data['redirect_url'] = SigninAPIView.return_url
                else:
                    SigninAPIView.return_url = None
                    response_data['redirect_url'] = 'home-api'

                return Response(response_data, status=status.HTTP_200_OK)
            else:
                error_message = 'Email or Password invalid !!'
        else:
            error_message = 'Email or Password invalid !!'

        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST) 
class ShopAPIView(APIView):
    def get_cart(self, request):
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            cart, created = Cart.objects.get_or_create(customer=customer)
        else:
            cart = None
        return cart

    def get(self, request):
        # Fetch categories and products
        category_id = request.GET.get('category')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category)
        else:
            products = Product.objects.filter(deleted_at__isnull=True)

        product_serializer = ProductSerializer(products, many=True)
        categories = Category.objects.all()
        category_serializer = CategorySerializer(categories, many=True)
        
        # Fetch cart items for the authenticated user
        cart = self.get_cart(request)
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            cart_item_serializer = CartItemSerializer(cart_items, many=True)
            cart_data = cart_item_serializer.data
        else:
            cart_data = []

        return Response({
            'categories': category_serializer.data,
            'products': product_serializer.data,
            'selected_category': category_id,
            'cart_items': cart_data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        product_id = request.data.get('product')
        action = request.data.get('action')  # 'add' or 'remove'

        customer_id = request.session.get('customer')
        if not customer_id:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer = get_object_or_404(Customer, id=customer_id)
        cart, created = Cart.objects.get_or_create(customer=customer)

        if product_id:
            product = get_object_or_404(Product, id=product_id)
            if action == 'add':
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not created:
                    cart_item.quantity += 1
                    cart_item.save()
            elif action == 'remove':
                cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                if cart_item:
                    if cart_item.quantity > 1:
                        cart_item.quantity -= 1
                        cart_item.save()
                    else:
                        cart_item.delete()

        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignupAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Ensure this view is accessible without authentication

    def get(self, request):
        return Response({'message': 'Signup GET request received'}, status=status.HTTP_200_OK)
    
    def post(self, request):
        postdata = request.data
        first_name = postdata.get('firstname')
        last_name = postdata.get('lastname')
        phone = postdata.get('phone')
        email = postdata.get('email')
        password = postdata.get('password')

        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            password=password
        )

        error_message = self.validateCustomer(customer)

        if not error_message:
            customer.password = make_password(customer.password)
            customer.save()
            tokens = get_tokens_for_user(customer)
            response_data = {
                'message': 'Registration successful',
                'refresh': tokens['refresh'],
                'access': tokens['access'],
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

    def validateCustomer(self, customer):
        error_message = None

        if not customer.first_name:
            error_message = "First Name Required"
        elif len(customer.first_name) < 4:
            error_message = "First Name must be greater than 4 characters"
        elif not customer.last_name:
            error_message = "Last Name Required"
        elif len(customer.last_name) < 3:
            error_message = "Last Name must be 3 characters long or more"
        elif not customer.phone:
            error_message = "Phone Number Required"
        elif len(customer.phone) < 10:
            error_message = "Phone number must be 10 characters long"
        elif len(customer.email) < 5:
            error_message = "Email must be 5 characters long"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", customer.email):
            error_message = "Enter Valid Email"
        elif len(customer.password) < 6:
            error_message = "Password must be 6 characters long"
        elif Customer.objects.filter(email=customer.email).exists():
            error_message = "Email Address Already Registered"

        return error_message
class SignoutAPIView(APIView):

    def post(self, request):
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            cart = customer.get_cart()
            request.session['cart'] = list(cart.products.values_list('id', flat=True))

        logout(request)

        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore

class CartAPIView(APIView):

    def get_cart(self, request):
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            cart, created = Cart.objects.get_or_create(customer=customer)
        else:
            cart = None
        return cart

    def get(self, request):
        cart = self.get_cart(request)
        if cart:
            cart_items = CartItem.objects.filter(cart=cart)
            serializer = CartItemSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        product_id = request.data.get('product')
        action = request.data.get('action')  # 'add' or 'remove'

        customer_id = request.session.get('customer')
        if not customer_id:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer = Customer.objects.get(id=customer_id)
        cart = customer.cart

        if product_id:
            product = get_object_or_404(Product, id=product_id)
            if action == 'add':
                cart.add_to_cart(product)
            elif action == 'remove':
                cart.remove_from_cart(product)

        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CategoryAPIView(APIView):

    def get(self, request, id):
        category = get_object_or_404(Category, id=id)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateCartAPIView(APIView):

    def get_cart(self, request):
        customer_id = request.session.get('customer')
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            cart, created = Cart.objects.get_or_create(customer=customer)
        else:
            cart = None
        return cart

    def post(self, request):
        customer_id = request.session.get('customer')
        if not customer_id:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        cart = self.get_cart(request)
        if not cart:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        for key, value in request.data.items():
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]
                quantity = int(value)
                product = get_object_or_404(Product, id=product_id)
                cart_item = CartItem.objects.filter(cart=cart, product=product).first()
                
                if quantity > 0:
                    if cart_item:
                        cart_item.quantity = quantity
                        cart_item.save()
                    else:
                        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                else:
                    if cart_item:
                        cart_item.delete()

        # Fetch updated cart items
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RemoveFromCartAPIView(APIView):
   
    def delete(self, request, product_id):
        cart = request.session.get('cart', {})
        cart.pop(str(product_id), None)
        request.session['cart'] = cart
        return Response({"cart": cart}, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import Order, Product, OrderItem
from .serializers import OrderSerializer
import razorpay
from django.utils import timezone

class CheckOutAPIView(APIView):
    serializer_class = OrderSerializer

    def get_cart_items(self, customer):
        cart_items = CartItem.objects.filter(cart__customer=customer)
        return cart_items

    def get(self, request):
        customer_id = request.session.get('customer')
        if not customer_id:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        customer = get_object_or_404(Customer, id=customer_id)
        orders = Order.get_orders_by_customer(customer_id).reverse()

        # Fetch cart items for the logged-in customer
        cart_items = self.get_cart_items(customer)
        cart_item_serializer = CartItemSerializer(cart_items, many=True)

        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        client = razorpay.Client(auth=('rzp_test_jo0inWyUOZon7N', 'YGWhPHfOQGQqgdtTtoFJO4tY'))
        payment = client.order.create({'amount': int(total_price * 100), 'currency': 'INR', 'payment_capture': '1'})

        order = Order(customer_id=customer_id, price=total_price, razorpay_payment_id=payment['id'])
        order.save()

        serialized_orders = OrderSerializer(orders, many=True).data

        context = {
            'orders': serialized_orders,
            'cart_items': cart_item_serializer.data,
            'total_price': total_price,
            'payment': payment
        }
        return Response(context)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            customer_id = request.session.get('customer')
            if not customer_id:
                return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

            customer = get_object_or_404(Customer, id=customer_id)
            cart_items = self.get_cart_items(customer)
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            order = Order.objects.filter(customer_id=customer_id, razorpay_payment_id=data.get('razorpay_order_id')).first()

            if order:
                order.first_name = data.get('first_name')
                order.last_name = data.get('last_name')
                order.address = data.get('address')
                order.city = data.get('city')
                order.state = data.get('state')
                order.postcode = data.get('postcode')
                order.phone = data.get('phone')
                order.price = total_price
                order.email = data.get('email')
                order.payment_method = data.get('payment_method')
                order.date = timezone.now()

                order.save()

                payment_status = self.process_payment(data.get('razorpay_payment_id'), data.get('razorpay_order_id'), data.get('razorpay_signature'))
                if payment_status == 'success':
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price * item.quantity
                        )
                    request.session['cart'] = {}
                    request.session.modified = True

                    return Response({'status': 'success'})
                else:
                    return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_payment(self, razorpay_payment_id, razorpay_order_id, razorpay_signature):
        client = razorpay.Client(auth=('rzp_test_jo0inWyUOZon7N', 'YGWhPHfOQGQqgdtTtoFJO4tY'))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            return 'failed'

        order = Order.objects.get(razorpay_payment_id=razorpay_order_id)
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_order_id = razorpay_order_id
        order.razorpay_signature = razorpay_signature
        order.paid = True
        order.save()

        return 'success'
    
class OrderAPIView(APIView):
    
    def get(self, request, format=None):
        customer_id = request.session.get('customer')
        if not customer_id:
            return Response({"error": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer = get_object_or_404(Customer, id=customer_id)
        orders = Order.objects.filter(customer=customer)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderItemsAPIView(APIView):
   
    def get(self, request, id):
        order_items = OrderItem.objects.filter(order_id=id)
        serializer = OrderItemSerializer(order_items, many=True)
        return Response(serializer.data)

# @csrf_exempt
# def process_payment(request):
#     if request.method == 'POST':
#         razorpay_payment_id = request.POST.get('razorpay_payment_id')
#         razorpay_order_id = request.POST.get('razorpay_order_id')
#         razorpay_signature = request.POST.get('razorpay_signature')

#         # Verify the payment signature
#         client = razorpay.Client(auth=('rzp_test_QyPXjDMWkihZcL', 'ei1pCmVOcNDHNtjn59rONSh6'))
#         params_dict = {
#             'razorpay_order_id': razorpay_order_id,
#             'razorpay_payment_id': razorpay_payment_id,
#             'razorpay_signature': razorpay_signature
#         }

#         try:
#             client.utility.verify_payment_signature(params_dict)
#         except razorpay.errors.SignatureVerificationError:
#             return JsonResponse({'status': 'failed'})

#         # Fetch the order created earlier and update it
#         try:
#             order = Order.objects.get(razor_pay_payment_id=razorpay_order_id)
#             order.razorpay_payment_id = razorpay_payment_id
#             order.razorpay_signature = razorpay_signature
#             order.save()

#             return JsonResponse({'status': 'success', 'redirect_url': '/order_success/'})
#         except Order.DoesNotExist:
#             return JsonResponse({'status': 'failed'})

#     return JsonResponse({'status': 'failed'})