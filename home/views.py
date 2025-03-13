from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib import messages
from .models import Product
# import xác thực (hàm đã viết ở file backends) và login là hàm của django
from django.contrib.auth import authenticate, login
from .models import UserClient
import random
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
    product_ao = []
    product_quan = []
    product_vay = []
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
        if product.type.category_id.name in ["Áo", "Ao"]:
            product_ao.append(product_data)
        if product.type.category_id.name in ["Quần", "Quan"]:
            product_quan.append(product_data)
        if product.type.category_id.name in ["Váy", "Vay"]:
            product_vay.append(product_data)
            
    product_random = []
    if product_list:
        num_random = min(5, len(product_list))
        random_product = random.sample(product_list, num_random)
        product_random = random_product
    product_random1 = []
    
    if product_list: 
        num_random = min(5, len(product_list))
        random_product = random.sample(product_list, num_random)
        product_random1 = random_product
    return render(request, 'home/home.html', {'products': product_list, 'product_ao': product_ao, 'product_quan': product_quan, 'product_vay': product_vay, 'product_random': product_random, 'product_random1': product_random1})


from django.shortcuts import render, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
import json
from .models import Product, Productvariant

class DecimalEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def product_detail(request, product_id):
    # Lấy thông tin sản phẩm
    product = get_object_or_404(Product, id=product_id)
   
    # Lấy tất cả các biến thể sản phẩm còn hàng
    variants = Productvariant.objects.filter(
        product_id=product_id,
        stock__gt=0
    )
   
    # Tổ chức dữ liệu variants theo màu sắc
    variants_by_color = {}
    for variant in variants:
        color = variant.color
        if color not in variants_by_color:
            variants_by_color[color] = {
                'sizes': [],
                'image': variant.image.url  # Lấy đường dẫn URL đầy đủ
            }
        variants_by_color[color]['sizes'].append({
            'id': variant.id,      # Thêm ID của variant
            'size': variant.size,
            'stock': variant.stock,
            'price': str(variant.price),  # Chuyển đổi Decimal thành string
        })
    
    # Chuyển đổi thành JSON sử dụng encoder tùy chỉnh
    variants_json = json.dumps(variants_by_color, cls=DecimalEncoder)
    
    return render(request, 'home/variants.html', {
        'product': product,
        'variants_json': variants_json,
        'variants_by_color': variants_by_color
    })
    
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, Productvariant, UserClient
import json

@require_POST
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'test': 'Hello World'})
        # return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng'}, status=401)
    
    try:
        data = json.loads(request.body)
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)
        
        # Kiểm tra dữ liệu đầu vào
        if not variant_id:
            return JsonResponse({'success': False, 'message': 'Thiếu thông tin biến thể sản phẩm'}, status=400)
        
        # Lấy user hiện tại (giả sử người dùng đã đăng nhập)
        user = UserClient.objects.get(username=request.user.username)
        
        # Kiểm tra và lấy biến thể sản phẩm
        try:
            variant = Productvariant.objects.get(id=variant_id)
        except Productvariant.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy biến thể sản phẩm'}, status=404)
        
        # Kiểm tra tồn kho
        if variant.stock < quantity:
            return JsonResponse({
                'success': False, 
                'message': f'Số lượng yêu cầu vượt quá tồn kho. Hiện chỉ còn {variant.stock} sản phẩm.'
            }, status=400)
        
        # Tìm hoặc tạo giỏ hàng
        cart, created = Cart.objects.get_or_create(user_id=user)
        
        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart_item, item_created = CartItem.objects.get_or_create(
            cart_id=cart,
            product_variant_id=variant,
            defaults={'quantity': quantity}
        )
        
        # Nếu sản phẩm đã tồn tại trong giỏ hàng, cập nhật số lượng
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Đếm số lượng sản phẩm trong giỏ hàng
        cart_count = CartItem.objects.filter(cart_id=cart).count()
        
        return JsonResponse({
            'success': True, 
            'message': 'Đã thêm sản phẩm vào giỏ hàng', 
            'cart_count': cart_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)