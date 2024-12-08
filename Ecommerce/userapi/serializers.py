from rest_framework import serializers
from custom_admin.models import Product, Category, Customer, Order, Product, OrderItem, CartItem

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'email', 'first_name', 'last_name','is_active','phone','last_login']  # Add other fields as necessary


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price']

    def to_representation(self, instance):
        # Override to_representation to calculate the total price
        representation = super().to_representation(instance)
        representation['price'] = instance.product.price * instance.quantity
        return representation

    
from rest_framework import serializers
# from ..models import Transaction


class RazorpayOrderSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    currency = serializers.CharField()


class TranscationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["razor_pay_payment_id", "razor_pay_order_id", "razor_pay_payment_signature", "price"]