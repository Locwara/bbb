# import thư viện BaseBackend
from django.contrib.auth.backends import BaseBackend
# import hàm check_password
from django.contrib.auth.hashers import check_password
# import UserClient từ model
from .models import UserClient


# Khởi tạo một đối tượng UserClientAuthBackend kế thừa từ thư viện BaseBackend
class UserClientAuthBackend(BaseBackend):
    # Tạo hàm authenticate truyền vào request, username và password cho none hết
    def authenticate(self, request=None, username=None, password=None, **kwargs):
        # kiểm tra
        try:
            # cho biến user = username trong database mà username đó phải trùng với username truyền vào
            user = UserClient.objects.get(username=username)
            # nếu mà mật khẩu được truyền vào trùng với mật khẩu của username đó trong database
            if check_password(password, user.password):
                # thì return là có user
                return user
            # check không đúng thì return rỗng
            return None
        # Trường hợp ngoại lệ User không tồn tại thì trả về None luôn
        except UserClient.DoesNotExist:
            return None
    # khỏi tạo hàm get_user để lấy user có id giống với id truyền vào
    def get_user(self, user_id):
        # Thực hiện trả về user trong database mà có id giống với id truyền vào
        try:
            return UserClient.objects.get(id=user_id)
        # Nếu không tồn tại thì trả về rỗng
        except UserClient.DoesNotExist:
            return None
        