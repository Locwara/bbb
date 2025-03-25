from django import template

register = template.Library()

@register.filter
def has_user_rating(item, user):
    return item.userrating_set.filter(user=user, product_variant=item.product_variant).exists()