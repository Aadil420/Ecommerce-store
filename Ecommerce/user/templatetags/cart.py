from django import template

register = template.Library()

def is_in_cart(product , cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
           return True
    return False
register.filter('is_in_cart',is_in_cart)



@register.filter
def cart_quantity(product, cart):
    return cart.get(str(product.id), 0)


@register.filter
def price_total(product, cart):
    return product.price * cart_quantity(product, cart)

@register.filter
def total_cart_price(products , cart):
    sum = 0 
    for p in products:
        sum += price_total(p , cart)
    return sum
# register.filter('total_cart_price',total_cart_price)

@register.filter
def calculate_total_order_price(order):
    total_price = 0
    order_items = order.order_items.all()  # Access related OrderItem instances using related_name
    for item in order_items:
        total_price += item.product.price * item.quantity
    return total_price
