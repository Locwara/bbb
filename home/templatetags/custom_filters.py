from django import template
from django.template.defaultfilters import floatformat
# Đăng ký thư viện template
register = template.Library()

# Tạo filter 'mul'
@register.filter(name='mul')
def mul(value, arg):
    """Nhân giá trị value với arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
    
    
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