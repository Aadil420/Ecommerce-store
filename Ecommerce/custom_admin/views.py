from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render
from .models import Category,Product,Customer,Order,OrderItem
from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('index')  # Redirect to dashboard if already authenticated

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            request.session.set_expiry(10)  # Set session expiry to 10 seconds
            return redirect('index')  # Redirect to dashboard on successful login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def admin_logout(request):
    logout(request)  # Logs out the user
    request.session.flush()  # Clear all session data
    return redirect('dash_login')  # Redirect to login page


def category_list(request):
    categories = Category.objects.all().order_by('-id')
    context = {'data': categories} 
    return render(request, 'category_table.html', context)

def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'

        existing_category = Category.objects.filter(name=name, deleted_at__isnull=True).first()
        if existing_category:
            error_msg = f"Category {name} already exists."
            return render(request, 'category_form.html', {'error': error_msg})
        else:
            category = Category.objects.create(name=name, description=description, is_active=is_active)
            return redirect("category_list")
    return render(request, 'category_form.html')


def category_edit(request, id):
    category = Category.objects.filter(id=id).first()
    print(id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'

        # Check for existing category with the same name that is not the current category
        existing_category = Category.objects.filter(name=name).exclude(id=id).first()
        if existing_category and existing_category.deleted_at is None:
            error_msg = f"Category {name} already exists"
            return render(request, 'category_edit_form.html', {'error': error_msg, 'category': category})
        else:
            category.name = name
            category.description = description
            category.is_active = is_active
            category.save()
            return redirect('category_list')

    return render(request, 'category_edit_form.html', {'category': category})

def order_items(request, id):
    order_items = OrderItem.objects.filter(order_id=id)
    return render(request, 'order_items.html', {'order_items': order_items})


def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.soft_delete()
    return redirect( request,'category_list')

def product_list(request):
    products = Product.objects.filter(deleted_at__isnull=True)
    return render(request, 'product_list.html', {'products': products})

def product_create(request):
    categories = Category.objects.all()
    context = {'data': categories}
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        category = Category.objects.get(id=category_id)
        
        product = Product.objects.create(
            name=name,
            price=price,
            category=category,
            description=description,
            image=image
        )
        return redirect("product_list")
    
    return render(request, 'product_create.html', context)

def product_edit(request, id):
    categories = Category.objects.all()
    product = Product.objects.filter(id=id).first()

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Update the product fields
        product.name = name
        product.price = price
        product.description = description

        if category_id:
            category = Category.objects.get(id=category_id)
            product.category = category

        if image:
            product.image = image

        product.save()
        return redirect('product_list')

    context = {
        'product': product,
        'data': categories
    }
    return render(request, 'product_edit.html', context)

def product_delete(request,id):
    product = get_object_or_404(Product, id=id)
    product.soft_delete()
    return redirect( 'product_list')

def customer_list(request):
    customers = Customer.objects.filter(deleted_at__isnull=True)
    return render(request, 'customer_list.html', {'customers': customers})


def customer_create(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_active = request.POST.get('is_active') == 'True'

        existing_customer = Customer.objects.filter(email=email, deleted_at__isnull=True).first()
        if existing_customer:
            error_msg = f"A customer with the email {email} already exists."
            return render(request, 'customer_create.html', {'error': error_msg, 'form_data': request.POST})
        else:
            customer = Customer.objects.create(first_name=first_name, last_name=last_name, phone=phone, email=email,password=password, is_active=is_active)
            customer.save()
            return redirect("customer_list")
    return render(request, 'customer_create.html')

def customer_edit(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_active = request.POST.get('is_active') == 'on'
        print(customer)
        # Check for existing customer with the same email that is not the current customer
        existing_customer = Customer.objects.filter(email=email).exclude(id=id).first()
        if existing_customer and existing_customer.deleted_at is None:
            error_msg = f"A customer with the email {email} already exists."
            return render(request, 'customer_edit.html', {'error': error_msg, 'customer': customer})
        else:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.phone = phone
            customer.email = email
            customer.password = password
            customer.is_active = is_active
            customer.save()
            return redirect('customer_list')

    return render(request, 'customer_edit.html', {'customer': customer})
        
def customer_delete(request, id):
    customer = get_object_or_404(Customer, id=id)
    customer.soft_delete()
    return redirect('customer_list')

def order_list(request):
    orders = Order.objects.filter(deleted_at__isnull=True)
    return render(request, 'order_list.html', {'orders': orders})

from django.shortcuts import render, redirect
from datetime import date  # Import date from datetime module

def order_create(request):
    product = Product.objects.all()
    customer = Customer.objects.all()

    if request.method == 'POST':
        product = request.POST.get('product')
        customer = request.POST.get('customer')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        status = request.POST.get('status')

        order = Order.objects.create(
            product_id=product,
            customer_id=customer,
            quantity=quantity,
            price=price,
            address=address,
            phone=phone,
            date=date,
            status=status
        )
        order.save()
        return redirect('order_list')

    context = {
        'product': product,
        'customer': customer,
    }
    return render(request, 'order_create.html', context)


def order_edit(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        order.product_id = request.POST.get('product_id')
        order.customer_id = request.POST.get('customer_id')
        order.quantity = request.POST.get('quantity')
        order.price = request.POST.get('price')
        order.address = request.POST.get('address')
        order.phone = request.POST.get('phone')
        order.date = request.POST.get('date')
        order.status = request.POST.get('status')
        order.save()
        return redirect('order_list')
    return render(request, 'order_edit.html', {'order': order})

def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    order.soft_delete()
    return redirect('order_list')

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    return render(request, 'category_view.html', {'category': category})

def customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'customer_view.html', {'customer': customer})

def product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_view.html', {'product': product})
    
def order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_view.html', {'order': order})

@csrf_exempt
def update_order_status(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
            return JsonResponse({'success': True})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Order does not exist'})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def dashboard(request):
    try:
        orders = Order.objects.filter(deleted_at__isnull=True).select_related('product', 'customer')
        products = Product.objects.filter(deleted_at__isnull=True)
    except Exception as e:
        # Log the error or handle it accordingly
        print(f"Error fetching data: {e}")
        orders = []
        products = []
    
    context = {
        'orders': orders,
        'products': products
    }
    return render(request, 'index.html', context)