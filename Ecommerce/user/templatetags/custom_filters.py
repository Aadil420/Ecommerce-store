from django import template

register = template.Library()

# @register.filter(name = 'currency')
def currency(number):
    return "₹"+str(number)

register.filter('currency',currency)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def multiply(number , number1):
    return number*number1


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)