from django import template
from home.models import UserRating
from django.template.defaultfilters import floatformat
from home.models import Feedback
# Đăng ký thư viện template
register = template.Library()

# Tạo filter 'mul'


    
    
@register.filter
def vn_currency(value):
    # Định dạng số, loại bỏ thập phân và đổi sang chuỗi
    value_str = floatformat(value, 0)
    # Chuyển chuỗi sang số nguyên để xử lý
    try:
        value_int = int(value_str.replace(',', '').replace('.', ''))
        # Định dạng với dấu chấm ngăn cách
        result = '{:,}'.format(value_int).replace(',', '.')
        return result
    except (ValueError, TypeError):
        return value_str
@register.filter
def filter_by_user(ratings, user):
    return ratings.filter(user=user)


@register.filter
def filter_by_variant(ratings, product_variant):
    return ratings.filter(product_variant=product_variant)

@register.filter
def has_rated(item, user):
    return item.userrating_set.filter(user=user).exists()

from django import template
from home.models import UserRating  # Import UserRating model



@register.filter
def check_existing_rating(order_item, user):
    return UserRating.objects.filter(
        user=user,
        product_variant=order_item.product_variant,
        order=order_item.order
    ).exists()
    
    
@register.filter
def check_existing_feedback(order, user):
    return Feedback.objects.filter(
        user=user,
        order=order
    ).exists()
    
    
    
@register.filter
def sub(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''

@register.filter
def div(value, arg):
    try:
        return value / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return ''