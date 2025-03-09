from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from .models import Product
# import xác thực (hàm đã viết ở file backends) và login là hàm của django
from django.contrib.auth import authenticate, login
from .models import UserClient

# Create your views here.



# khởi tạo hàm đăng ký
def register_view(request):
    #nếu nhận được một yêu cầu và có phương thức là POST
    if request.method == 'POST':
        # Thì tạo một biến form đại diện cho form với khung giống với form đã được khai báo trong forms.py
        #form đó sẽ có dữ liệu từ yêu cầu nhận được (POST)
        form = RegisterForm(request.POST)
        # Nếu form đó hợp lệ
        if form.is_valid():
            #print ra teminal để dev check
            print("Cleaned data:", form.cleaned_data) 
            # Kiểm tra nếu password(đã qua kiểm tra cleaned_data) không giống rpassword tức là nhập lại mật khẩu
            if form.cleaned_data['password'] != form.cleaned_data['rpassword']:
                # Thì báo lỗi mật khẩu không khớp
                messages.error(request, 'Mật khẩu không khớp!')
                # Trả kết quả lỗi cho trang đăng ký
                return render (request, 'home/register.html', {'form':form})
            # Trường hợp còn lại thì tạo một biến user để lưu form nhưng không commit qua database
            user = form.save(commit = False)
            # thực hiện mã hóa mật khẩu bằng hàm set_password(hàm đã viết bên models)
            user.set_password(form.cleaned_data['password'])
            # sau đó tiến hành commit lên database
            user.save()
            # thông báo thành công
            messages.success(request, 'Đăng ký thành công!')
            # chuyển hướng đến trang đăng nhập
            return redirect('login')
        # Nếu form không hợp lệ thì báo lỗi
        else:
            print("Form errors:", form.errors)
    # Nếu method không phải POST thì trả lại một form đăng ký rỗng
    else:
        form = RegisterForm()
    # Hàm này sẽ đc render tới trang đăng ký để run
    return render(request, 'home/register.html', {'form': form})

# khỏi tạo hàm đăng nhập
def login_view(request):
    # Nếu nhận được một yêu cầu và có phương thức là POST
    if request. method == 'POST':
        # Tạo hai biến username và password để lưu dữ liệu nhận được từ phương thức POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Tạo biến user và dùng hàm authenticate để kiểm tra đăng nhập
        user = authenticate(request=request, username=username, password=password)
        # Nếu user tồn tại 
        if user is not None:
            # tiến hành login thông báo thành công
            login(request, user)
            messages.success(request, 'Đăng nhập thành công')
            # lưu id của user đã đăng nhập vào session(để thuật tiện cho việc bảo mật)
            request.session['user_id'] = user.id 
            # chuyển hướng đến home
            return redirect('home')
        # Nếu user không có thì báo lỗi về trang login
        else:
            return render(request, 'home/login.html', {'error': 'Invalid credentials'})
    # Nếu method không phải POST thì trả lại trang đăng nhập thông báo lỗi
    messages.error(request, 'Không có phương thức nào')
    return render (request, 'home/login.html')

def format_currency(value):
    return f"{int(value):,}".replace(",", ".") + " đ"

def home(request):
    # cho biến products lấy hết tất cả các variant liên quan bằng prefetch_related
    #prefetch_ralated dùng cho quan hệ one to many trong trường hợp này
    products = Product.objects.prefetch_related('variants').select_related('id_discount_percentage').all()
    
    
    
    # Thêm thông tin hình ảnh vào từng sản phẩm
    product_list = []
    #duyệt từng phần tử của products
    for product in products:
        # Lấy hình ảnh của biến thể đầu tiên (nếu có)
        first_variant = product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        
        #tính giá giảm nè
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        # một dic để lưu biến tham chiếu qua html là các sản phẩm và hình 
        product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam)
        }
        product_list.append(product_data)
    return render(request, 'home/home.html', {'products': product_list})


