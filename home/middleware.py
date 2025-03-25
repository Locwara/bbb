from django.shortcuts import redirect
from django.urls import reverse
from home.models import UserClient

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Danh sách các URL công khai không cần xác thực
        public_urls = [
            reverse('login'),
            reverse('register'),
            reverse('home'),
            reverse('forgot_password'),
            reverse('google_callback'),
            '/google-login/',
            '/accounts/google/login/callback/',
            '/media/',
            '/favicon.ico',
            '/social-auth/',
            '/social-auth/complete/facebook/',
            '/social-auth/login/facebook/',
            reverse('index'),
            reverse('danh_sach_san_pham'),

            # 🟢 Thêm PayPal IPN và webhook vào danh sách công khai
            reverse('paypal-ipn'), 
            reverse('payment_done'),
            reverse('payment_canceled'),
            '/paypal/webhook/',
        ]

        # Các URL động (chỉ cần bắt đầu bằng chuỗi nhất định)
        allowed_prefixes = [
            '/login-client/product/',
            '/login-client/cart/update/',
            '/login-client/cart/remove/',
            '/paypal/',
        ]

        # Kiểm tra nếu URL là công khai hoặc có prefix được phép
        is_public_url = request.path in public_urls or any(request.path.startswith(prefix) for prefix in allowed_prefixes)

        # Bỏ qua kiểm tra nếu là request từ PayPal (IPN/Webhook)
        if is_public_url:
            return self.get_response(request)

        # Kiểm tra user từ session
        user_id = request.session.get('user_id') if hasattr(request, "session") else None
        if user_id:
            try:
                request.user = UserClient.objects.get(id=user_id)
            except UserClient.DoesNotExist:
                request.user = None
        else:
            request.user = None

        # Nếu không có user và không phải URL công khai, chuyển hướng đến trang đăng nhập
        if request.user is None:
            return redirect('login')

        return self.get_response(request)
