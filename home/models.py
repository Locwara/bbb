from django.db import models
# import Abs va Per để có thể dùng cách hàm có Django có sẵn
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
# import hàm make_password của django
from django.contrib.auth.hashers import make_password
# Create your models here.


# Tạo một model UserClient kế thừa từ models của django
class UserClient(models.Model):
    # Khỏi tạo cách biến bằng cách trường tương ứng có trong table trong database
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    phone_number = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=255)
    auth_type = models.CharField(max_length=20, choices=[('email', 'Email'), ('facebook', 'Facebook'), ('tranditional', 'Tranditional')], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateField(blank=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    # hàm xác thực luôn trả về true :)))
    @property
    def is_authenticated(self):
        return True
    # lớp Meta dùng để liên kết với table users trong database
    class Meta:
        db_table = 'users'
    # Hàm set_password làm thủ công do django không hỗ trợ
    def set_password(self, raw_password):
        # make_password để mã hóa mật khẩu
        self.password = make_password(raw_password)
     
     
     

         
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = 'Category'

class Producttype(models.Model):
    CATEGORY_ID_CHOICES =[
        ('Vay', 'Váy'),
        ('Quan', 'Quần'),
        ('Ao', 'Áo')

    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    category_id =models.ForeignKey(Category, on_delete=models.CASCADE, db_column='category_id')

    class Meta:
        db_table ='producttype'

class discount_percentage(models.Model):
    id = models.AutoField(primary_key=True)
    percent =  models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'discount_percentage'
class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    description2 = models.TextField()
    base_price= models.DecimalField(max_digits=10, decimal_places=2)
    id_discount_percentage = models.ForeignKey(discount_percentage, related_name='discount_percentage', on_delete=models.CASCADE, db_column='id_discount_percentage')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type =models.ForeignKey(Producttype, on_delete=models.CASCADE, db_column='type')

    class Meta:
        db_table = 'product'

class Productvariant(models.Model):
    id = models.AutoField(primary_key=True)
    product =models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=20)
    color = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/%Y/%m/%d')
    stock = models.IntegerField(max_length=11)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
   


    class Meta:
        db_table = 'productvariant'