
from django.urls import path
from . import views as home
urlpatterns = [
    # đường dẫn cho trang đăng ký
    path('register/', home.register_view, name='register'),
    # đường dẫn cho trang đăng nhập
    path('login/', home.login_view, name='login'),
    # đường dẫn cho trang chủ
    path('home/', home.home, name='home'),
    # đường dẫn dùng để dẫn đến chi tiết sản phẩm
    path('product/<int:product_id>/', home.product_detail, name='product_detail'),
    # đường dẫn để xử lý thêm sản phẩm vào giỏ hàng
    path('cart/add/', home.add_to_cart, name='add_to_cart'),
    # đường dẫn giỏ hàng
    path('cart/', home.cart, name='cart'),
    path('cart/update/<int:item_id>/', home.update_cart_item, name='update_cart'),
    path('cart/remove/<int:item_id>/', home.remove_from_cart, name='remove_from_cart'),
    # đường dẫn đăng xuất
    path('logout/', home.logout, name='logout'),
    # đường dẫn trang thông tin cá nhân
    path('profile/', home.profile, name='profile'),
    # đường dẫn trang đổi mật khẩu
    path('change-password/', home.change_password, name='change_password'),
    # đường dẫn trang quên mật khẩu
    path('forgot-password/', home.forgot_password, name="forgot_password"),
    path('google-login/', home.google_login, name='google_login'),
    path('checkout/', home.checkout_view, name='checkout'),
    path('order-confirmation/', home.order_confirmation, name='order_confirmation'),
    path('orders/', home.order_list, name='order_list'),
    path('orders/<int:order_id>/', home.order_detail, name='order_detail'),
    path('profile/update/', home.update_profile, name='update_profile'),
    path('order/<int:order_id>/cancel/', home.cancel_order, name='cancel_order'),
    path('paypal/', home.process_paypal, name='process_paypal'),
    path('rate-order-item/<int:order_item_id>/', home.rate_order_item, name='rate_order_item'),
    path('feedback/create/<int:order_id>/', home.create_feedback, name='create_feedback'),
    path('danh-sach-san-pham/', home.danh_sach_san_pham, name='danh_sach_san_pham'),
    

]