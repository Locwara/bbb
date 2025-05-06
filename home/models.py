from django.db import models
# import Abs va Per để có thể dùng cách hàm có Django có sẵn
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
# import hàm make_password của django
from django.contrib.auth.hashers import make_password, check_password
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
    auth_type = models.CharField(max_length=20, choices=[('email', 'Email'), ('facebook', 'Facebook'), ('tranditional', 'Tranditional'), ('google', 'Google')], null=True)
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
    def check_password(self, raw_password):
        # So sánh mật khẩu
        return check_password(raw_password, self.password)
    
     
     
     

         
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = 'category'

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
        
        
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey('UserClient', on_delete=models.CASCADE, db_column='user_id')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cart'

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, db_column='cart_id', related_name='items')
    product_variant_id = models.ForeignKey('Productvariant', on_delete=models.CASCADE, db_column='product_variant_id', related_name='cart_items')
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cartitem'
        
from django.db import models
from django.contrib.auth.models import User

# models.py
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    STATUS_CHOICES = (
        ('pending', 'Đang xử lý'),
        ('accept', 'Đang giao hàng'),
        ('done', 'Đã hoàn thành'),
        ('cancelled', 'Đã hủy'),
    )
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Thêm trường này
    payment_method = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_phone = models.CharField(max_length=15)
    payment_status = models.BooleanField(default=False)
    re_pay = models.CharField(max_length=20, null=True, blank=True)  # Trường này để lưu thông tin thanh toán lại
    stk = models.CharField(max_length = 50, null=True, blank=True)  # Trường này để lưu thông tin thanh toán lại
    class Meta:
        db_table = 'orders'
    

# models.py
from django.db import models

class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='items', on_delete=models.CASCADE)  # Liên kết với Order
    product_variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE)  # Liên kết với sản phẩm
    quantity = models.PositiveIntegerField()  # Số lượng sản phẩm
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # Giá sản phẩm
    created_at = models.DateTimeField(auto_now_add=True)  # Thời gian tạo

    def total_price(self):
        return self.quantity * self.unit_price  # Tính tổng tiềnteTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orderitem'
        
        
# models.py
class Address(models.Model):
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    ward = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[('visible', 'Hiển thị'), ('hidden', 'Ẩn')], default='visible')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'address'

    def save(self, *args, **kwargs):
        # Tự động hủy tất cả địa chỉ mặc định khác nếu đánh dấu mặc định
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Voucher(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=5, decimal_places=2)  # Phần trăm giảm giá
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to
    
    def __str__(self):
        return f"{self.code} - {self.discount_amount}%"
    
    class Meta:
        db_table = 'voucher'
        
class UserRating(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(UserClient, on_delete=models.CASCADE, related_name='ratings')
    product_variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'userrating'
        verbose_name = 'User Rating'
        verbose_name_plural = 'User Ratings'
        
    def __str__(self):
        return f"{self.user.username} - {self.product_variant.name} ({self.rating}/5)"
class Feedback(models.Model):
    user = models.ForeignKey('UserClient', on_delete=models.CASCADE)
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'feedback'

    def __str__(self):
        return f"Feedback for Order {self.order_id}"
    
    
class UsedVoucher(models.Model):
    """
    Model to track vouchers used by users
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserClient', on_delete=models.CASCADE, related_name='used_vouchers')
    voucher = models.ForeignKey('Voucher', on_delete=models.CASCADE, related_name='used_by_users')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'used_voucher'
        unique_together = ('user', 'voucher')  # Ensure a user can't use the same voucher multiple times

    def __str__(self):
        return f"{self.user.username} - {self.voucher.code}"