# import UserClient từ model
from .models import UserClient
# import thư viện forms từ django
from django import  forms

# Tạo một đối tượng Form đăng ký kế thừa từ modelForm
class RegisterForm(forms.ModelForm):
    # Tạo hai biến password và rpassword = hai form dạng nhập là password với dạng text 
    password = forms.CharField(widget=forms.PasswordInput)
    rpassword = forms.CharField(widget=forms.PasswordInput)
    
    # một class Meta dùng để thao tác với table trong database thông qua models
    class Meta: 
        model = UserClient
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'password']    
        
        
