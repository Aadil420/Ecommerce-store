from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
# Create your models here.

class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
class Category(models.Model):
    image = models.ImageField(upload_to='uploads/categories/',blank=True, null=True)
    name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def get_all_categories(include_deleted=False):
        if include_deleted:
            return Category.objects.all()
        return Category.objects.filter(deleted_at__isnull=True)

    objects = CategoryManager()

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        self.deleted_at = None
        self.save()


    def __str__(self):
        return self.name

from django.db import models
from django.utils import timezone

class CustomerManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Customers must have an email address")

        customer = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

    def create_superuser(self, email, first_name, last_name, password=None):
        customer = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        customer.is_admin = True
        customer.save(using=self._db)
        return customer

class Customer(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=13, default='', blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=500)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name='custom_admin_customer_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_admin_customer_permissions', blank=True)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_staff(self):
        return self.is_admin
    
    def register(self):
        self.save()
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return None

    def isExits(self):
        if Customer.objects.filter(email = self.email):
            return True
        return False

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()

    def restore(self):
        self.deleted_at = None
        self.is_active = True
        self.save()

    def get_cart(self):
        cart, created = Cart.objects.get_or_create(customer=self)
        return cart

from django.db import models
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/products/',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Product.objects.filter(deleted_at__isnull=True)
    
    @staticmethod
    def get_all_product_by_category_id(category_id):
        if category_id:
            return Product.objects.filter(category_id=category_id)
        else:
            return Product.objects.filter(deleted_at__isnull=True)

from django.db import models
from django.utils import timezone

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('delete', 'Delete'),
    ]
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE,blank=True,null=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=50, default='', blank=True,null=True)
    phone = models.CharField(max_length=50, default='', blank=True,null=True)
    email = models.EmailField(blank=True,null=True)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=100, null=True, blank=True)
    paid = models.BooleanField(default=False)

    def place_order(self):
        self.save()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')
    
    def soft_delete(self):
        self.status = 'delete'
        self.deleted_at = timezone.now()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


# from django.db import models
# from django.contrib.auth.models import User

# class Admin_Panel_AuthToken(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     token = models.CharField(max_length=40, unique=True)
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.user.email} - {self.token}'

#     class Meta:
#         db_table = 'admin_panel_authToken'


class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')
    
    def __str__(self):
        return f"{self.customer.first_name} {self.customer.last_name}"
    
    def add_to_cart(self, product, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)
        if not created:
            cart_item.quantity += quantity
        cart_item.price = cart_item.quantity * product.price
        cart_item.save()

    def remove_from_cart(self, product):
        CartItem.objects.filter(cart=self, product=product).delete()

    def clear_cart(self):
        CartItem.objects.filter(cart=self).delete()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name}"