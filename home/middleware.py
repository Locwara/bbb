# file middleware.py dùng để chặn đăng nhập
from django.shortcuts import redirect
from django.urls import reverse
from home.models import UserClient

# tạo một đối tượng phần mềm trung gian phục vụ cho việt xác thực 
class AuthenticationMiddleware:
    # lưu phản hồi
    def __init__(self, get_response):
        self.get_response = get_response
    # khi có request gửi tới thì nó sẽ lấy url 
    def __call__(self, request):
        public_urls = [
            reverse('login'),
            reverse('register'),
        ]

        # Kiểm tra nếu request.session tồn tại 
        user_id = request.session.get('user_id') if hasattr(request, "session") else None
        #  Nếu có tồn tại user trong sesssion
        if user_id:
            try:
                # Kiểm tra xem thk này có trong database không
                request.user = UserClient.objects.get(id=user_id)
            # Nếu nó có trong session nhưng không có trong database thì user = None :>
            except UserClient.DoesNotExist:
                request.user = None
        # Nếu không có thk nào trong session thì None luôn
        else:
            request.user = None
        # Kiểm tra nếu mà path trong yêu cầu gửi đi không nằm trong url công khai 
        # và kiểm tra user ở trên á mà ra None => cho về trang login hết
        if request.path not in public_urls and request.user is None:
            return redirect('login')
        # Nếu không vấn đề j thì sẽ lấy phản hồi tiếp theo
        return self.get_response(request)
