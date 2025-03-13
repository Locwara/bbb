
from django.urls import path
from . import views as home
urlpatterns = [
    # đường dẫn cho trang đăng ký
    path('register/', home.register_view, name='register'),
    # đường dẫn cho trang đăng nhập
    path('login/', home.login_view, name='login'),
    # đường dẫn cho trang chủ
    path('home/', home.home, name='home'),
    path('product/<int:product_id>/', home.product_detail, name='product_detail'),
    path('cart/add/', home.add_to_cart, name='add_to_cart'),

]