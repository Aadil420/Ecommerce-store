from django.shortcuts import render , redirect , HttpResponseRedirect
from django.views import View
from django.contrib.auth.hashers import  check_password
from django.contrib.auth.hashers import make_password
from custom_admin.models import Customer,Product,Category,Order,OrderItem
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth import logout
import re
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

class Home(View):

    # def post(self , request):
    #     product = request.POST.get('product')
    #     remove = request.POST.get('remove')
    #     cart = request.session.get('cart')
    #     if cart:
    #         quantity = cart.get(product)
    #         if quantity:
    #             if remove:
    #                 if quantity<=1:
    #                     cart.pop(product)
    #                 else:
    #                  cart[product] = quantity - 1
    #             else:
    #                 cart[product] = quantity + 1
                

    #         else:
    #          cart[product] = 1 
    #     else:
    #         cart = {}
    #         cart[product] = 1


    #     request.session['cart'] = cart
    #     print('cart' , request.session['cart'])
    #     return redirect('homepage')
    
    
    def get(self, request):
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
        products = None
        
        categories = Category.get_all_categories()
            
        categoryId = request.GET.get('category')
        if categoryId:
                products = Product.get_all_product_by_category_id(categoryId)
        else:
                products = Product.get_all_products()
        data = {}
        data['products'] = products
        data['categories'] = categories
        print('You are' , request.session.get('email'))
        return render(request, 'home.html', data)


class Signin(View):
    return_url = None

    def get(self, request):
        # Initialize the cart in session if it doesn't exist
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}

        Signin.return_url = request.GET.get('return_url')
        return render(request, 'signin.html')

    def post(self , request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Signin.return_url:
                    return HttpResponseRedirect(Signin.return_url)
                else:
                    Signin.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'Email or Password invalid !!'
        else:
            error_message = 'Email or Password invalid !!'

        print(email, password)
        return render(request, 'signin.html', {'error': error_message})

def signout(request):
    # Save cart data before logging out
    cart = request.session.get('cart', {})

    # Perform the logout
    logout(request)

    # Restore the cart data after logout
    request.session['cart'] = cart

    return redirect('signin')  # Redirect to the sign-in page or any other page

class signup(View):
    def get(self , request):
          return render(request, 'signup.html')
    
    def post(self , request):
         postdata = request.POST
         first_name = postdata.get('firstname')
         last_name = postdata.get('lastname')
         phone = postdata.get('phone')
         email = postdata.get('email')
         password = postdata.get('password')
         # validation
     
         value = {
             'first_name': first_name,
             'last_name': last_name,
             'phone': phone,
             'email': email
         }
         error_message = None
       
     
              
                 
     
     
         customer = Customer(first_name=first_name,
                         last_name=last_name,
                         phone=phone,
                         email=email,
                         password=password)
     
         error_message = self.validateCustomer(customer)
     
     
         if not error_message:
              print(first_name, last_name, phone, email, password)
              customer.password = make_password(customer.password)
              customer.register()
              return redirect('homepage')
     
         else:
              data = {
             'error': error_message,
             'values': value
          }
              return render(request, 'signup.html', data)
         
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
        elif customer.isExits():
            error_message = "Email Address Already Registered"

        return error_message

class ShopView(View):
    def get(self, request):
        category_id = request.GET.get('category')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            products = Product.objects.filter(category=category)
        else:
            products = Product.objects.filter(deleted_at__isnull=True)
        categories = Category.objects.all()
        return render(request, 'shop.html', {'categories': categories, 'products': products, 'selected_category': category_id})

    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        if product:
            quantity = cart.get(product, 0)
            if remove:
                if quantity > 1:
                    cart[product] = quantity - 1
                else:
                    cart.pop(product, None)
            else:
                cart[product] = quantity + 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('shop')


class CartView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        if cart:
            ids = list(cart.keys())
            products = Product.objects.filter(id__in=ids)
        else:
            products = []
        return render(request, 'cart.html', {'products': products})
    def post(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return render(request, 'cart.html', {'error_message': 'Your cart is empty'})
        else:
            return redirect('checkout')

def category_view(request, id):
    category = get_object_or_404(Category, id=id)
    return render(request, 'shop.html', {'category': category})

from django.urls import reverse
def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                product_id = key.split('_')[1]
                quantity = int(value)
                if quantity > 0:
                    cart[product_id] = quantity
                else:
                    cart.pop(product_id, None)
        request.session['cart'] = cart
        return redirect('cart')  # Redirect to the cart page or any other page

    return redirect('shop')  # Fallback redirect

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    return redirect('cart')
class CheckOut(View):
    def get(self, request):
        customer = request.session.get('customer')
        if not customer:
            return redirect('signin')

        orders = Order.get_orders_by_customer(customer).reverse()

        cart = request.session.get('cart', {})
        cart_product_details = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                cart_product_details.append({'product': product, 'quantity': quantity})
            except Product.DoesNotExist:
                del cart[product_id]
        request.session['cart'] = cart
        products = Product.objects.filter(id__in=list(cart.keys()))
        total_price = sum(product.price * cart.get(str(product.id)) for product in products)
        total_amount_in_paise = int(total_price * 100)
        
        client = razorpay.Client(auth=('rzp_test_jo0inWyUOZon7N', 'YGWhPHfOQGQqgdtTtoFJO4tY'))
        payment = client.order.create({'amount': total_amount_in_paise, 'currency': 'INR', 'payment_capture': '1'})
        
        order = Order(customer_id=customer, price=total_price, razorpay_payment_id=payment['id'])
        order.save()
        
        context = {
            'orders': orders,
            'cart_product_details': cart_product_details,
            'products': products,
            'payment': payment
        }
        return render(request, 'checkout.html', context)

    @csrf_exempt
    def post(self, request):
        customer_id = request.session.get('customer')
        if not customer_id:
            return redirect('signin')

        cart = request.session.get('cart', {})
        products = Product.objects.filter(id__in=list(cart.keys()))
        total_price = sum(product.price * cart.get(str(product.id)) for product in products)
        order = Order.objects.filter(customer_id=customer_id, razorpay_payment_id=request.POST.get('razorpay_order_id')).first()

        if order:
            order.first_name = request.POST.get('first_name')
            order.last_name = request.POST.get('last_name')
            order.address = request.POST.get('address')
            order.city = request.POST.get('city')
            order.state = request.POST.get('state')
            order.postcode = request.POST.get('postcode')
            order.phone = request.POST.get('phone')
            order.price = total_price
            order.email = request.POST.get('email')
            order.payment_method = request.POST.get('payment_method')
            order.date = timezone.now()
            
            order.save()

            # Process the payment
            payment_status = self.process_payment(request.POST.get('razorpay_payment_id'), request.POST.get('razorpay_order_id'), request.POST.get('razorpay_signature'))
            if payment_status == 'success':
                cart = request.session.get('cart')
                products = Product.objects.filter(id__in=list(cart.keys()))
                for product in products:
                    quantity = cart.get(str(product.id))
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price * quantity
                    )
                # Empty the cart after order is placed
                request.session['cart'] = {}
                request.session.modified = True  # Ensure the session is saved

                return redirect('user_orders')
            else:
                # Handle payment failure scenario
                return JsonResponse({'status': 'failed'})

        return redirect('user_orders')
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

    
class OrderView(View):
    def get(self , request ):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print(f"ssdfdasdsd{orders}")
        orders = orders.reverse
        return render(request , 'user_orders.html'  , {'orders' : orders})
    
def order_items(request, id):
    order_items = OrderItem.objects.filter(order_id=id)
    return render(request, 'user_order_items.html', {'order_items': order_items})
