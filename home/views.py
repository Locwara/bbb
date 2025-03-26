from django.shortcuts import render, redirect
#import các đối tượng từ form
from .forms import RegisterForm, ChangePasswordForm, ForgotPasswordForm
#import thư viện messages để dùng cho việc hiển thị thông báo
from django.contrib import messages
from .models import Product, UserClient, UserRating
# import xác thực (hàm đã viết ở file backends) và login là hàm của django
from django.contrib.auth import authenticate, login
#import hàm thư viện random trong python dùng để random sản phẩm và mật khẩu mới
import random
# dùng để chuyển dữ liệu sang dạng vector phục vụ cho xử lý content based filtering
from sklearn.feature_extraction.text import TfidfVectorizer
# hàm tính độ tương đồng phục vụ cho xử lý content based filtering
from sklearn.metrics.pairwise import cosine_similarity
# Import thư viện pandas với tên là pd
import pandas as pd
#import  get_object_or_404 một là lấy được đối tượng 2 là trả về lỗi mã 404
from django.shortcuts import render, get_object_or_404
# hỗ trợ các chuyển đổi các kiểu dữ liệu của django mà python không sử dụng
from django.core.serializers.json import DjangoJSONEncoder
# thư viện Decimal dùng để chuyển đổi tính toán chính xác   
from decimal import Decimal
# json dùng để chuyển một đối tượng sang một chuỗi json có thể cho dễ đọc hơn hoặc gửi dữ liệu đi
import json
# từ models import Product và Productvariant
from .models import Product, Productvariant


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
# dùng để định dạng khi có giá trị truyền vào 
# hàm sẽ trả về giá trị int và định dạng theo đơn vị ngàn, chục ngàn, trăm ngàn,... + đ
def format_currency(value):
    return f"{int(value):,}".replace(",", ".") + " đ"
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F
import random

from .models import (
    Product, Category, Producttype, 
    Productvariant, Order, OrderItem
)

# Utility function for currency formatting
def format_currency(amount):
    return "{:,.0f}".format(amount).replace(",", ".")

def home(request):
    # Lấy tất cả sản phẩm với thông tin liên quan
    products = Product.objects.prefetch_related('variants').select_related('id_discount_percentage').all()
    
    # Lấy top 5 sản phẩm bán chạy nhất
    top_products = (
        Product.objects
        .filter(variants__orderitem__order__status='done')
        .annotate(
            total_sold_quantity=Sum('variants__orderitem__quantity', 
                                    filter=Q(variants__orderitem__order__status='done'))
        )
        .order_by('-total_sold_quantity')
        .prefetch_related('variants')
        .select_related('id_discount_percentage')
        [:5]  # Giới hạn top 5 sản phẩm
    )

    # Danh sách để chứa các sản phẩm
    product_list = []
    product_ao = []
    product_quan = []
    product_vay = []
    top_products_list = []

    # Xử lý sản phẩm
    for product in products:
        # Lấy hình ảnh của biến thể đầu tiên (nếu có)
        first_variant = product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        # Tính toán giảm giá
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        
        # Tạo dictionary sản phẩm
        product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam)
        }
        
        # Thêm vào danh sách chung
        product_list.append(product_data)
        
        # Phân loại sản phẩm theo danh mục
        if product.type.category_id.name in ["Áo", "Ao"]:
            product_ao.append(product_data)
        if product.type.category_id.name in ["Quần", "Quan"]:
            product_quan.append(product_data)
        if product.type.category_id.name in ["Váy", "Vay"]:
            product_vay.append(product_data)

    # Xử lý sản phẩm bán chạy
    for product in top_products:
        first_variant = product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        
        top_product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam),
            'total_sold_quantity': product.total_sold_quantity
        }
        
        top_products_list.append(top_product_data)

    # Sản phẩm ngẫu nhiên
    product_random = random.sample(product_list, min(5, len(product_list))) if product_list else []
    product_random1 = random.sample(product_list, min(5, len(product_list))) if product_list else []

    # Lấy ID các danh mục
    ao_category = Category.objects.get(name='Áo')
    quan_category = Category.objects.get(name='Quần')
    vay_category = Category.objects.get(name='Váy')
    
    # Truyền context
    context = {
        'products': product_list,
        'product_ao': product_ao, 
        'product_quan': product_quan,
        'product_vay': product_vay, 
        'product_random': product_random, 
        'product_random1': product_random1,
        'top_products': top_products_list,
        'ao_category_id': ao_category.id,
        'quan_category_id': quan_category.id,
        'vay_category_id': vay_category.id,
    }
    
    return render(request, 'home/home.html', context)

def product_detail(request, product_id):
    # Lấy sản phẩm chi tiết
    product = get_object_or_404(Product.objects.prefetch_related('variants'), pk=product_id)
    
    # Lấy các biến thể của sản phẩm
    variants = product.variants.all()
    
    # Tính toán giảm giá
    discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
    giagoc = product.base_price
    giagiam = giagoc - (giagoc * discount_percent/100)
    
    # Lấy các sản phẩm liên quan (cùng loại)
    related_products = Product.objects.filter(
        type=product.type
    ).exclude(pk=product_id)[:4]
    
    # Xử lý sản phẩm liên quan
    related_products_list = []
    for related_product in related_products:
        first_variant = related_product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        related_discount_percent = related_product.id_discount_percentage.percent if related_product.id_discount_percentage else 0
        related_giagoc = related_product.base_price
        related_giagiam = related_giagoc - (related_giagoc * related_discount_percent/100)
        
        related_products_list.append({
            'product': related_product,
            'variant_image': first_variant_image,
            'discount_percent': related_discount_percent,
            'giagoc': format_currency(related_giagoc),
            'giagiam': format_currency(related_giagiam)
        })
    
    context = {
        'product': product,
        'variants': variants,
        'giagoc': format_currency(giagoc),
        'giagiam': format_currency(giagiam),
        'discount_percent': discount_percent,
        'related_products': related_products_list
    }
    
    return render(request, 'product/product_detail.html', context)

def category_products(request, category_id):
    # Lấy danh mục
    category = get_object_or_404(Category, pk=category_id)
    
    # Lấy tất cả sản phẩm thuộc danh mục
    products = Product.objects.filter(
        type__category_id=category
    ).prefetch_related('variants').select_related('id_discount_percentage')
    
    # Phân trang
    paginator = Paginator(products, 12)  # 12 sản phẩm trên mỗi trang
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    # Xử lý sản phẩm
    product_list = []
    for product in products_page:
        first_variant = product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        
        product_list.append({
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam)
        })
    
    context = {
        'category': category,
        'products': product_list,
        'page_obj': products_page
    }
    
    return render(request, 'product/category_products.html', context)# cho một đối tượng kế thừ từ thư viện DjangoJSONEncoder 
class DecimalEncoder(DjangoJSONEncoder):
    # đặt một hàm tên là default
    def default(self, obj):
        # nếu đối tượng thuộc kiểu Decimal thì trả về True và ngược lại
        if isinstance(obj, Decimal):
            # nếu là decimal thì chuyển đối tượng đó thành chuỗi
            return str(obj)
        # dùng cho khi mà có một đối tượng không thuộc hỗ trợ của python thì sẽ tự động gọi hàm default của DjangoJSONEncoder
        return super().default(obj)
    
    
from django.db.models import Avg
# Tạo một hàm tên product_detail với biến request và product_id(dùng để truyền vào id của product)
def product_detail(request, product_id):
    # cho biến products đại diện cho tất cả sản phẩm và được trỏ khóa ngoại tới hai table là productvariant và discount_percentage 
    # thông qua prefetch_related(trường hợp ở đây là dùng quan hệ one-to-many), select_related(trường hợp ở đây là dùng cho quan hệ many-to-one)
    products = Product.objects.prefetch_related('variants').select_related('id_discount_percentage').all()
    # tạo mội danh sách rỗng tên product_list
    product_list = []
    
    # cho product lặp để lấy tường sản phẩm trong products
    for product in products:
        # biến first_variant sẽ lấy một biến thể đầu tiên thông qua tên khóa ngoại ở mỗi lần lặp
        first_variant = product.variants.first()
        # biến first_variant_image sẽ lấy đường dẫn hình ảnh của variant đầu tiên nếu sản phẩm đó có biến thể và biến thể đó có đường dẫn hình ảnh nếu không thỏa = None
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        # biến discount lấy số phần trăm giảm giá từ cột percent của bản discount_percentage thông qua id_discount_percentage ở mỗi lần lặp nếu không có trả về 0
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        
        # biến giagoc sẽ lấy giá từ cột base_price
        giagoc = product.base_price
        # biến giagiam sẽ lấy giá gốc - giá gốc nhân với phần trăm giảm giá
        giagiam = giagoc - (giagoc * discount_percent/100)
        # tạo một list tên product_data để lưu các thông tin vừa xử lí ở trên
        product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            # dùng hàm format_currency để định dạng giá
            'giagoc': format_currency(giagoc),
            # dùng hàm format_currency để định dạng giá
            'giagiam': format_currency(giagiam)
        }
        # sau đó sẽ add product_data vào product_list
        product_list.append(product_data)

    # Get main product details
    product = get_object_or_404(Product, id=product_id)
    
    # cho biến variants lấy những biến thể sản phẩm với điều kiện lọc là product_id bằng với product_id mà hàm nhận được
    variants = Productvariant.objects.filter(
        product_id=product_id,
        # cột stock phải lớn hơn 0
        stock__gt=0
    )
    
    # Sắp sếp biến thể theo màu sắc
    # tạo một list trống
    variants_by_color = {}
    # cho biến variant là từng biến thể trong variants
    for variant in variants:
        # cho biến color lấy màu của variant
        color = variant.color
        # nếu màu không có trong dic varants_by_color thì màu đó sẽ được lưu vào dic
        if color not in variants_by_color:
            # dic variants_by_color sẽ lưu dic color bên trong dic color sẽ có một list sizes và biến image
            variants_by_color[color] = {
                'sizes': [],
                'image': variant.image.url
            }
        # dựa vào key dic là color để thêm các thông tin vào size
        variants_by_color[color]['sizes'].append({
            # sẽ add tất cả id, size, stock, price của variant nào mà có màu trùng với key, sẽ được add vào dic color
            'id': variant.id,
            'size': variant.size,
            'stock': variant.stock,
            'price': str(round(variant.price, 0)),
            'discount_percent': str(round(variant.product.id_discount_percentage.percent, 0)),
            # giá giảm sẽ được tính bằng giá gốc - giá gốc nhân với phần trăm giảm giá và làm tròn 2 chữ số
            'discount_price': str(round(variant.price - (variant.price * discount_percent/100), 0))
        })
    
    # cho một biến variants_json = để convert opject variant sang dữ liệu text của json
    # cls dùng để chỉ nếu có dữ liệu nào không hợp lệ với python thì sẽ gọi tới opject DecimalEncoder và thực hiện hàm default ở trỏng
    variants_json = json.dumps(variants_by_color, cls=DecimalEncoder)
    product_ratings = UserRating.objects.filter(product_variant__product=product).select_related('user', 'product_variant')
    for rating in product_ratings:
        print(f"Rating: {rating.rating}, User: {rating.user.username}")

    average_rating = product_ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    # biến recommended_products sẽ gọi hàm để thực hiện hàm lấy các sản phẩm gợi ý nó sẽ truyền vào product_id, và danh sách sản phẩm, sau khi xử lý sẽ được trả về
    recommended_products = get_recommended_products(product_id, product_list)
    
    # đây là một giải pháp thay thế nếu hệ thống gợi ý bị lỗi
    # tạo một list product_random rỗng 
    product_random = []
    # nếu product_list tồn tại sản phẩm 
    if product_list:
        # tạo một biến num_random lấy nhỏ nhất là 5 và độ dài là product_list
        num_random = min(5, len(product_list))
        # biến random_product lấy dữ liệu random sample giúp cho sản phẩm random không bị trùng lặp và product_list không bị sáo trộn
        random_product = random.sample(product_list, num_random)
        # gán list product_random = các sản phẩm đã xáo trộn
        product_random = random_product
    # rende những thông tin đã xử lý qua trang template
    return render(request, 'home/variants.html', {
        'product': product,
        'variants_json': variants_json,
        'variants_by_color': variants_by_color,
        'products': product_list,
        'product_random': product_random,
        'recommended_products': recommended_products,
        'product_ratings': product_ratings,
        'average_rating': round(average_rating, 1),  # Làm tròn 1 chữ số thập phân
        'total_ratings': product_ratings.count()
    })

def get_recommended_products(product_id, product_list):
    """
    Get recommended products based on content-based filtering
    
    Args:
        product_id: ID of the current product
        product_list: List of processed product data 
    
    Returns:
        List of recommended product data
    """
    # thử thực hiện
    try:
        # tạo một list rỗng products_data
        products_data = []
        # tạo một dic rỗng product_id_map
        product_id_map = {}  
        # cho biến i và product_data lặp, dùng enumerate sẽ tự động tăng biến i mà không cần tăng i thủ công
        for i, product_data in enumerate(product_list):
            # cho biến product = product trong dic product_data
            product = product_data['product']
            # lưu với mỗi id của sản phẩm thì tương ứng với chỉ mục nào trong vòng lặp
            product_id_map[product.id] = i
            
            # dữ liệu để tính toán độ tương đồng
            # biến category lấy attr của đối tượng category của bản product nếu có và ngược lại là rỗng, hoặc nếu mà không tồn tại attr của product thì nó sẽ trả về rỗng thay vì None
            category = getattr(product, 'category', '') or ''
            # tương tự như trên
            description = getattr(product, 'description', '') or ''
            # tương tự như trên
            name = getattr(product, 'name', '') or ''
            # tương tự như trên nhưng dạng float và nếu không tồn tại thì trả về 0
            price = float(product.base_price or 0)
            
            # Price category
            # danh mục giá
            # nếu giá nhỏ hơn 50000 thì cho biến price_category = giá thấp
            if price < 500000:
                price_category = "giá thấp"
            # nếu giá nhỏ hơn 150000 thì price_category = giá trung bình
            elif price < 1500000:
                price_category = "giá trung bình" 
            # trường hợp còn lại thì cho price_category = giá cao
            else:
                price_category = "giá cao"
            # cho biến combined_features lấy một chuỗi dữ liệu chứ thống tin danh mục, mô tả, tên, giá của sản phẩm với dạng chứ thường
            combined_features = f"{str(category).lower()} {str(name).lower()} {str(description).lower()} {price_category}"
            # add dic gồm id và chuỗi thông tin vào list products_data
            products_data.append({
                'id': product.id,
                'combined_features': combined_features
            })
        
        # Create DataFrame chuyển list gồm các dic thành dạng bảng
        df = pd.DataFrame(products_data)
        
        # Create TF-IDF matrix
        # chuyển đổi dữ liệu dạng text thành vertor để dễ so sánh và stop_words sẽ bỏ qua các từ như and, the, is, in để tập trung vào các từ quan trọng
        tfidf = TfidfVectorizer(stop_words='english')
        # biến tfidf_matrix lấy dữ liệu của cột là văn bản của combined_features, 
        # dùng fit_transform  để tạo ma trận tf-idf để giúp dễ tính độ tương đồng giữa các sản phẩm
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        # biến consine_sim hàm cosine_similarity dùng biến tfidf_matrix để tính độ tương đồng
        cosine_sim = cosine_similarity(tfidf_matrix)
        
        # thử lấy gợi ý
        try:
            # cho idx lấy sản phẩm trong id_map xem có id giống id truyền vào không
            idx = product_id_map.get(product_id)
            # nếu mà không có thì return ra danh sách rỗng
            if idx is None:
                # If product not found in our map, return empty list
                return []
                
            # cho biến sim_scores là một danh sách chứa các sản phẩm đã tính độ tương đồng, biến truyền vào cosine_sim sẽ là sản phẩm làm gốc
            sim_scores = list(enumerate(cosine_sim[idx]))
            # sắp xếp lại danh sách lấy phần tử thứ hai trong mỗi cặp của list để sắp xếp, reverse = True tức là sắp xếp giảm dần
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            # tiến hàng lấy tối đa 5 phần tử nếu nó không phải là idx thì lấy tránh gợi ý lại sản phẩm gốc
            sim_scores = [x for x in sim_scores if x[0] != idx] [:5]
            # duyệt qua product_indeces và lấy phần tử đầu ở mỗi tuple
            product_indices = [i[0] for i in sim_scores]
            
            # Get recommended products data
            # tạo một list để lưu
            recommended_products = []
            # cho biến idx là biến duyệt product_indices
            for idx in product_indices:
                # duyệt từng product_data
                for product_data in product_list:
                    # nếu mà product trong product_data có sản phẩm có id trùng với  id của bản ghi đã được xử lý dữ liệu
                    # thì sẽ add sản phẩm product_data từ product_list vào recommended_products
                    if product_data['product'].id == df.iloc[idx]['id']:
                        recommended_products.append(product_data)
                        break
            # trả về list recommended_product đã hoàn thiện
            return recommended_products
        # lỗi trong quá trình lấy gợi ý
        except Exception as e:
            # tin lỗi ra
            print(f"Error in recommendation system: {str(e)}")
            return []
        # lỗi khi thực hiện quá trình khác
    except Exception as e:
        # in lỗi ra
        print(f"Error setting up recommendation system: {str(e)}")
        return []
    
# import JsonResponse dùng để khi chuyển dữ liệu sẽ chuyển san dạng JSON
from django.http import JsonResponse
# import hàm require_POST tác dụng chỉ cho phép hàm nhận POST
from django.views.decorators.http import require_POST
from .models import Cart, CartItem, Productvariant, UserClient
# import thư viện json
import json
#chỉ cho phép hàm nhận POST
@require_POST
# tạo hàm add_to_cart truyền vào biến request để xử lý thêm vào giỏ hàng
def add_to_cart(request):
    # nếu user_id không có trong session  thì sẽ trả về một dic gồm lỗi và tin nhắn chuyến sang json rồi mới gửi, mã lỗi 401
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để thêm sản phẩm vào giỏ hàng'}, status=401)
    # thử
    try:
        # biến data lấy dữ liệu từ request.body và chuyển từ text thành json
        data = json.loads(request.body)
        # biến variant_id lấy id của biến thể sản phẩm từ data
        variant_id = data.get('variant_id')
        # biến quantity lấy số lượng sản phẩm từ data
        quantity = data.get('quantity', 1)
        
        # Kiểm tra dữ liệu đầu vào
        if not variant_id:
        # trả về  một dic gồm lỗi và tin nhắn chuyến sang json rồi mới gửi, mã lỗi 400
            return JsonResponse({'success': False, 'message': 'Thiếu thông tin biến thể sản phẩm'}, status=400)
        # Lấy user hiện tại (giả sử người dùng đã đăng nhập)
        user = UserClient.objects.get(username=request.user.username)
        # Kiểm tra và lấy biến thể sản phẩm
        try:
            # biến variant lấy biến thể sản phẩm từ bảng Productvariant thông qua id
            variant = Productvariant.objects.get(id=variant_id)
            # nếu không tìm thấy biến thể sản phẩm thì trả về  một dic gồm lỗi và tin nhắn chuyến sang json rồi mới gửi, mã lỗi 404
        except Productvariant.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy biến thể sản phẩm'}, status=404)
        
        # Kiểm tra tồn kho
        # nếu số lượng sản phẩm yêu cầu lớn hơn số lượng tồn kho thì trả về  một dic gồm lỗi và tin nhắn chuyến sang json rồi mới gửi, mã lỗi 400
        if variant.stock < quantity:
            return JsonResponse({
                'success': False, 
                'message': f'Số lượng yêu cầu vượt quá tồn kho. Hiện chỉ còn {variant.stock} sản phẩm.'
            }, status=400)
        
        # Tìm hoặc tạo giỏ hàng
        # biến cart lấy giỏ hàng từ bảng Cart thông qua user_id nếu không có thì tạo mới
        cart, created = Cart.objects.get_or_create(user_id=user)
        
        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        cart_item, item_created = CartItem.objects.get_or_create(
            cart_id=cart,
            product_variant_id=variant,
            defaults={'quantity': quantity}
        )
        
        # Nếu sản phẩm đã tồn tại trong giỏ hàng và có số lượng nhỏ hơn tồn kho thì cộng thêm số lượng bằng với số lượng tồn kho
        if not item_created:
            cart_item.quantity = min(cart_item.quantity + quantity, variant.stock)
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
    
    
from django.shortcuts import render
from .models import Cart, CartItem

def cart(request):
    user_id = request.session.get('user_id')
    context = {'cart_items': [], 'total_price': 0}
    
    if user_id:
        try:
            # Sử dụng prefetch_related với tên trường chính xác từ model
            cart = Cart.objects.prefetch_related(
                'items__product_variant_id__product'  # Chú ý: product_variant_id__product
            ).get(user_id=user_id)
            
            cart_items = []
            
            for item in cart.items.all():
                # Truy cập qua trường product_variant_id (đúng tên trong model)
                product_variant = item.product_variant_id  
                product = product_variant.product  # Giả sử ProductVariant có FK tới Product
                
                cart_items.append({
                    'id': item.id,
                    'product_name': product.name,
                    'image_url': product_variant.image.url if product_variant.image else '/static/default-image.jpg',
                    'quantity': item.quantity,
                    'price': product_variant.price - (product_variant.price * item.product_variant_id.product.id_discount_percentage.percent/100),
                    'total': ( product_variant.price - (product_variant.price * item.product_variant_id.product.id_discount_percentage.percent/100)) * item.quantity,
                    'size': product_variant.size,  # Giả sử có trường size  
                    'color': product_variant.color  # Giả sử có trường color
                })
            
            context['cart_items'] = cart_items
            context['total_price'] = sum(item['total'] for item in cart_items)
            context['total_items'] = sum(item['quantity'] for item in cart_items)
            
        except Cart.DoesNotExist:
            pass
    
    return render(request, 'home/cart.html', context)

# Update quantity
def update_cart_item(request, item_id):
    if request.method == 'POST':
        try:
            item = CartItem.objects.get(id=item_id, cart_id__user_id=request.session.get('user_id'))
            new_quantity = int(request.POST.get('quantity', 1))
           
            if new_quantity > 0 and new_quantity <= item.product_variant_id.stock:
                item.quantity = new_quantity
                item.save()
            else:
                # Nếu số lượng không hợp lệ, thông báo lỗi và hiện số lượng hiện tại trên thông báo
                messages.error(request, f'Số lượng không hợp lệ. Số lượng hiện tại còn lại của mẫu này là: {item.quantity}')
                
                
        except CartItem.DoesNotExist:
            pass
            
    return redirect('cart')

# Remove item
# chỉ cho phép hàm nhận POST và truyền vào item_id
# viết lại hàm remove_from_cart và print lỗi đầy đủ


#viết lại hàm remove_from_cart với biến request và item_id không dùng post
def remove_from_cart(request, item_id):
    # thử
    try:
        # biến item lấy dữ liệu từ bảng CartItem thông qua id và cart_id__user_id
        item = CartItem.objects.get(id=item_id, cart_id__user_id=request.session.get('user_id'))
        # xóa item
        item.delete()
        messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng')  
    # lỗi
    except CartItem.DoesNotExist:
        # in ra lỗi
        print(f"Error removing item from cart: {str(e)}")
    # chuyển hướng về trang cart
    return redirect('cart')

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UpdateProfileForm

def profile(request):
    # Existing code remains the same
    user = request.user
    
    # Get default address
    default_address = Address.objects.filter(user=user, is_default=True).first()
    
    # Get order statistics
    completed_orders = Order.objects.filter(user=user, status='done').count()
    pending_orders = Order.objects.filter(user=user, status='pending').count()
    accept_orders = Order.objects.filter(user=user, status='accept').count()
    cancelled_orders = Order.objects.filter(user=user, status='cancelled').count()
    
    context = {
        'user': user,
        'default_address': default_address,
        'orders_completed': completed_orders,
        'orders_pending': pending_orders, 
        'orders_cancelled': cancelled_orders,
        'orders_accept': accept_orders,
        'total_orders': completed_orders + pending_orders + cancelled_orders
    }
    
    return render(request, 'home/profile.html', context)

def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thông tin tài khoản đã được cập nhật thành công!')
            return redirect('profile')
    else:
        form = UpdateProfileForm(instance=request.user)
    
    return render(request, 'home/update_profile.html', {'form': form})
def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']  # Xóa user_id khỏi session
    return redirect('home')  # Chuyển hướng đến trang chủ

def change_password(request):
    if not request.session.get('user_id'):
        return redirect('login')  # Chuyển hướng nếu người dùng chưa đăng nhập

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']

            # Lấy người dùng hiện tại từ session
            user = UserClient.objects.get(id=request.session['user_id'])

            # Kiểm tra mật khẩu cũ
            if user.check_password(old_password):  # Sử dụng phương thức check_password
                user.set_password(new_password)  # Đổi mật khẩu mới
                user.save()
                messages.success(request, 'Đổi mật khẩu thành công!')
                return redirect('home')
            else:
                messages.error(request, 'Mật khẩu cũ không đúng.')
    else:
        form = ChangePasswordForm()

    return render(request, 'home/change_password.html', {'form': form})
from django.conf import settings
import string
from django.core.mail import send_mail
def send_custom_email(subject, message, from_email, recipient_list):
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)
    
    body = MIMEText(message)
    msg.attach(body)
    
    try:
        print("Kết nối đến SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        print("Bắt đầu TLS...")
        server.starttls()
        print("Đăng nhập...")
        server.login('lethanhloc2612004@gmail.com', 'gqhn khbs wxzl ydgc')
        print("Gửi email...")
        server.send_message(msg)
        print("Đóng kết nối...")
        server.quit()
        return True
    except Exception as e:
        print(f"Chi tiết lỗi: {e}")
        return False  # Trả về False thay vì raise exception
def generate_password():
    """Tạo mật khẩu ngẫu nhiên 12 ký tự"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(12))

from django.core.mail import send_mail
from smtplib import SMTPAuthenticationError, SMTPException
import socket

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = UserClient.objects.filter(email=email).first()
            
            if user:
                # Tạo mật khẩu mới
                new_password = generate_password()
                
                # Lưu mật khẩu mới vào biến tạm thời
                temp_password = new_password
                
                # Cập nhật mật khẩu
                user.set_password(new_password)
                user.save()
                
                print(f"Đã đặt mật khẩu mới cho user {user.username}")
                
                subject = 'Mật khẩu mới cho tài khoản của bạn'
                message = f"""Xin chào {user.username},

Bạn vừa yêu cầu đặt lại mật khẩu cho tài khoản của mình trên {settings.SITE_NAME}.
Dưới đây là thông tin đăng nhập mới của bạn:

Username: {user.username}
Mật khẩu mới: {temp_password}

Vui lòng đăng nhập tại {settings.SITE_URL} và đổi mật khẩu ngay sau khi nhận được email này.

Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng liên hệ với chúng tôi ngay.

Trân trọng,
Ban quản trị {settings.SITE_NAME}"""

                print("Chuẩn bị gửi email...")
                
                try:
                    # Sử dụng hàm send_custom_email thay vì send_mail
                    sent = send_custom_email(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email]
                    )
                    
                    if sent:
                        print(f"Email đã được gửi đến {email}")
                        messages.success(
                            request, 
                            f'Mật khẩu mới đã được gửi đến email của bạn ({email}). Vui lòng kiểm tra email và đăng nhập lại.'
                        )
                    else:
                        # Trường hợp hàm trả về False
                        print("Hàm gửi email trả về False")
                        messages.error(
                            request,
                            'Không thể gửi email với mật khẩu mới. Vui lòng liên hệ quản trị viên.'
                        )
                        # Tùy chọn: Hiển thị mật khẩu mới trên trang (chỉ nên dùng trong môi trường phát triển)
                        messages.info(request, f'Mật khẩu mới (DEV MODE): {temp_password}')
                    
                # Giữ lại các khối except như cũ...
                except Exception as e:
                    print(f"Chi tiết lỗi gửi email: {str(e)}")
                    messages.error(
                        request,
                        f'Có lỗi xảy ra khi gửi email: {str(e)}. Vui lòng liên hệ quản trị viên để được hỗ trợ.'
                    )
                    # Tùy chọn: Hiển thị mật khẩu mới trên trang (chỉ nên dùng trong môi trường phát triển)
                    messages.info(request, f'Mật khẩu mới (DEV MODE): {temp_password}')
                
                return redirect('login')
            else:
                messages.error(
                    request,
                    'Email này không tồn tại trong hệ thống. Vui lòng kiểm tra lại.'
                )
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'home/forgot_password.html', {'form': form})

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from .models import UserClient
from .utils import verify_google_token

def google_login(request):
    if request.method == 'POST':
        try:
            token = request.POST.get('id_token')
            if not token:
                return JsonResponse({'success': False, 'error': 'Token không được cung cấp'}, status=400)
                
            user_info = verify_google_token(token)
            
            if not user_info:
                return JsonResponse({'success': False, 'error': 'Token không hợp lệ'}, status=400)
            
            email = user_info.get('email')
            # Tạo hoặc lấy người dùng từ bảng riêng biệt
            user, created = UserClient.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'auth_type': 'google',
                    'password': '',
                }
            )
            
            # Lưu thông tin người dùng vào session
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            
            return JsonResponse({'success': True, 'redirect': '/home/'})
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return render(request, 'home/login.html')


from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from .models import UserClient  # Thay thế bằng model của bạn
from .utils import verify_google_token  # Hàm xác thực token

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import UserClient

import requests
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from .models import UserClient

def google_callback(request):
    print("----- Bắt đầu xử lý callback -----")
    code = request.GET.get('code')
    print(f"Code nhận được: {code}")

    # Trao đổi code lấy token
    token_url = 'https://oauth2.googleapis.com/token'
    data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': 'http://127.0.0.1:8000/accounts/google/login/callback/',
        'grant_type': 'authorization_code'
    }
    
    print("----- Gửi yêu cầu lấy token tới Google -----")
    response = requests.post(token_url, data=data)
    print(f"Phản hồi từ Google (token): {response.status_code}, {response.text}")
    print(f"Phản hồi từ Google (token): {response.status_code}, {response.text}")
    if not response.ok:
        print(f"Lỗi khi trao đổi code: {response.status_code}, {response.text}")
        return JsonResponse({'success': False, 'error': 'Failed to get token'}, status=400)
    
    token_data = response.json()
    access_token = token_data.get('access_token')
    print(f"Access token nhận được: {access_token}")
    
    # Lấy thông tin người dùng
    user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    user_response = requests.get(user_info_url, headers=headers)
    print(f"Phản hồi từ Google (user info): {user_response.status_code}, {user_response.text}") 
    
    if not user_response.ok:
        print(f"Lỗi khi lấy thông tin người dùng: {user_response.status_code}, {user_response.text}")
        return JsonResponse({'success': False, 'error': 'Failed to get user info'}, status=400)
    
    user_info = user_response.json()
    print(f"Thông tin người dùng từ Google: {user_info}")
    
    email = user_info.get('email')
    if not email:
        return JsonResponse({'success': False, 'error': 'Email not found in user info'}, status=400)
    
    # Tạo hoặc lấy người dùng
    user, created = UserClient.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
            'auth_type': 'google',
            'password': '',  # Bỏ qua hoặc đặt giá trị mặc định
        }
    )
    print(f"User: {user}, Created: {created}")
    
    # Lưu thông tin vào session
    request.session['user_id'] = user.id
    request.session['email'] = user.email
    request.session.save()
    print(f"User ID trong session: {request.session.get('user_id')}")
    print(f"Email trong session: {request.session.get('email')}")
    
    # Chuyển hướng sau khi đăng nhập thành công
    return redirect('home')


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import Address, Order

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Address, Order

# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Address, Order, CartItem, OrderItem
from .models import Order, OrderItem, Address, Cart, CartItem, Voucher
        
from django.utils import timezone
def checkout_view(request):
    # Đảm bảo user đã đăng nhập
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để thanh toán')
        return redirect('login')
    
    # Biến lưu trữ thông tin voucher
    applied_voucher = None
    discount_amount = 0
    discount_value = 0
    
    # Xử lý selected_items từ giỏ hàng
    selected_items = []
    if request.method == 'POST' and 'selected_items' in request.POST:
        try:
            # Parse chuỗi JSON thành list
            items_str = request.POST.get('selected_items', '[]')
            raw_items = json.loads(items_str)
            
            # Lọc và chuyển đổi các giá trị thành số nguyên
            selected_items = []
            for item in raw_items:
                try:
                    item_id = int(item) if isinstance(item, str) else item
                    selected_items.append(item_id)
                except (ValueError, TypeError):
                    pass
        except (json.JSONDecodeError, ValueError):
            selected_items = []
        
        # Lưu vào session để sử dụng sau
        request.session['selected_items'] = selected_items
    else:
        # Sử dụng dữ liệu từ session nếu có
        selected_items = request.session.get('selected_items', [])
    
    # Kiểm tra nếu không có sản phẩm nào được chọn
    if not selected_items:
        messages.error(request, 'Vui lòng chọn ít nhất một sản phẩm để thanh toán')
        return redirect('cart')
    
    # Lấy giỏ hàng của người dùng
    try:
        cart = Cart.objects.get(user_id=request.user)
        
        # Lọc ra chỉ những sản phẩm đã được chọn
        cart_items = CartItem.objects.filter(cart_id=cart, id__in=selected_items)
        
        # Kiểm tra nếu không có sản phẩm nào được lọc ra
        if not cart_items.exists():
            messages.error(request, 'Không tìm thấy sản phẩm đã chọn trong giỏ hàng')
            return redirect('cart')
            
        # Tính tổng tiền cho các sản phẩm đã chọn
        total_amount = sum(
            item.quantity * (
                item.product_variant_id.price - 
                (item.product_variant_id.price * item.product_variant_id.product.id_discount_percentage.percent / 100)
            ) 
            for item in cart_items
        )
        
        # Lưu giá trị tổng gốc (trước khi áp dụng voucher)
        original_total = float(total_amount)
        
        # Lưu vào session để sử dụng sau khi redirect
        request.session['total_amount'] = float(total_amount)
        
    except Cart.DoesNotExist:
        messages.error(request, 'Không tìm thấy giỏ hàng')
        return redirect('cart')
    
    # Tính giá sau khi giảm cho mỗi sản phẩm
    for cart_item in cart_items:
        cart_item.discounted_price = cart_item.product_variant_id.price - (
            cart_item.product_variant_id.price * cart_item.product_variant_id.product.id_discount_percentage.percent / 100
        )
    
    # Lấy tất cả địa chỉ của người dùng
    user_addresses = Address.objects.filter(user=request.user).order_by('-is_default')
    
    # Lấy địa chỉ mặc định nếu có
    default_address = Address.objects.filter(user=request.user, is_default=True).first()
    
    # Xử lý khi người dùng nhập voucher
    if request.method == 'POST' and 'apply_voucher' in request.POST:
        voucher_code = request.POST.get('voucher_code', '').strip()
        if voucher_code:
            try:
                # Kiểm tra voucher hợp lệ (có tồn tại, còn hạn sử dụng)
                current_time = timezone.now()
                voucher = Voucher.objects.get(
                    code=voucher_code,
                    valid_from__lte=current_time,
                    valid_to__gte=current_time
                )
                
                # Lưu thông tin voucher vào session
                request.session['voucher_id'] = voucher.id
                request.session['voucher_code'] = voucher.code
                request.session['voucher_discount'] = float(voucher.discount_amount)
                
                messages.success(request, f'Áp dụng mã giảm giá "{voucher_code}" thành công!')
                
                # Chuyển hướng để tránh gửi lại form khi refresh
                return redirect('checkout')
                
            except Voucher.DoesNotExist:
                messages.error(request, 'Mã giảm giá không hợp lệ hoặc đã hết hạn!')
    
    # Xử lý khi người dùng gỡ bỏ voucher
    if request.method == 'POST' and 'remove_voucher' in request.POST:
        if 'voucher_id' in request.session:
            del request.session['voucher_id']
        if 'voucher_code' in request.session:
            del request.session['voucher_code']
        if 'voucher_discount' in request.session:
            del request.session['voucher_discount']
        
        messages.success(request, 'Đã gỡ bỏ mã giảm giá!')
        return redirect('checkout')
    
    # Lấy thông tin voucher từ session nếu có
    if 'voucher_id' in request.session:
        try:
            applied_voucher = Voucher.objects.get(id=request.session['voucher_id'])
            discount_amount = float(request.session['voucher_discount'])
            
            # Tính giảm giá theo phần trăm
            discount_value = original_total * (discount_amount / 100)
            total_amount = original_total - discount_value
            
        except Voucher.DoesNotExist:
            # Xóa thông tin voucher không hợp lệ
            if 'voucher_id' in request.session:
                del request.session['voucher_id']
            if 'voucher_code' in request.session:
                del request.session['voucher_code']
            if 'voucher_discount' in request.session:
                del request.session['voucher_discount']
    
    # Biến để lưu địa chỉ được chọn
    selected_address = None
    
    # Xử lý form địa chỉ và tạo đơn hàng
    
    if request.method == 'POST' and ('street' in request.POST or 'selected_address' in request.POST):
        # Lấy số điện thoại từ form
        customer_phone = request.POST.get('sdt', '')
        
        # Kiểm tra số điện thoại
        if not customer_phone:
            messages.error(request, 'Vui lòng nhập số điện thoại')
            context = {
                'cart_items': cart_items,
                'total_amount': total_amount,
                'user_addresses': user_addresses,
                'default_address': default_address,
                'applied_voucher': applied_voucher,
                'original_total': original_total,
                'discount_amount': discount_amount,
                'discount_value': discount_value
            }
            return render(request, 'home/checkout.html', context)
            
        # Xác định tab nào đang được sử dụng
        using_tab = request.POST.get('using_tab', '')
        
        # Kiểm tra xem người dùng có đang sử dụng "thêm địa chỉ mới" không và đã điền đầy đủ thông tin chưa
        is_new_address_valid = all([
            request.POST.get('street'),
            request.POST.get('ward'),
            request.POST.get('district'),
            request.POST.get('city')
        ])
        
        # Xử lý theo tab người dùng đang sử dụng
        if using_tab == 'new_address' and is_new_address_valid:
            # Người dùng đang sử dụng địa chỉ mới và đã nhập đầy đủ thông tin
            street = request.POST.get('street')
            ward = request.POST.get('ward')
            district = request.POST.get('district')
            city = request.POST.get('city')
            
            # Xử lý giá trị checkbox is_default
            is_default = request.POST.get('is_default') == 'on'
            
            # Nếu đánh dấu là địa chỉ mặc định, cập nhật các địa chỉ khác
            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            # Tạo địa chỉ mới
            selected_address = Address.objects.create(
                user=request.user,
                street=street,
                ward=ward,
                district=district,
                city=city,
                is_default=is_default
            )
        elif using_tab == 'saved_addresses' and request.POST.get('selected_address'):
            # Người dùng đang sử dụng địa chỉ đã lưu
            try:
                address_id = int(request.POST.get('selected_address'))
                selected_address = Address.objects.get(id=address_id, user=request.user)
                
                # Kiểm tra nếu người dùng đánh dấu địa chỉ này làm mặc định
                if request.POST.get('make_default') == 'on' and not selected_address.is_default:
                    # Cập nhật tất cả địa chỉ khác thành không mặc định
                    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
                    # Đặt địa chỉ này làm mặc định
                    selected_address.is_default = True
                    selected_address.save()
            except (ValueError, Address.DoesNotExist):
                messages.error(request, 'Địa chỉ không hợp lệ')
                context = {
                    'cart_items': cart_items,
                    'total_amount': total_amount,
                    'user_addresses': user_addresses,
                    'default_address': default_address,
                    'applied_voucher': applied_voucher,
                    'original_total': original_total,
                    'discount_amount': discount_amount,
                    'discount_value': discount_value
                }
                return render(request, 'home/checkout.html', context)
        else:
            # Trường hợp không có địa chỉ hợp lệ
            error_message = ''
            if using_tab == 'new_address':
                error_message = 'Vui lòng điền đầy đủ thông tin địa chỉ mới'
            elif using_tab == 'saved_addresses':
                error_message = 'Vui lòng chọn một địa chỉ đã lưu'
            else:
                error_message = 'Vui lòng chọn hoặc nhập địa chỉ giao hàng'
                
            messages.error(request, error_message)
            context = {
                'cart_items': cart_items,
                'total_amount': total_amount,
                'user_addresses': user_addresses,
                'default_address': default_address,
                'applied_voucher': applied_voucher,
                'original_total': original_total,
                'discount_amount': discount_amount,
                'discount_value': discount_value
            }
            return render(request, 'home/checkout.html', context)
        payment_method = request.POST.get('payment_method')
        # Nếu đã có địa chỉ hợp lệ, tiến hành tạo đơn hàng
        if selected_address:
            # Tạo order với thông tin voucher và số điện thoại
            order = Order.objects.create(
                user=request.user,  
                address=selected_address,
                total_amount=total_amount,
                discount_amount=discount_value,
                payment_method=payment_method,
                status='pending',
                customer_phone=customer_phone
            )
            
            # Chuyển sản phẩm từ giỏ hàng sang order - giữ nguyên code
            if cart_items:
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_variant=cart_item.product_variant_id,
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product_variant_id.price - (
                            cart_item.product_variant_id.price * 
                            cart_item.product_variant_id.product.id_discount_percentage.percent / 100
                        ) 
                    )
                    
                # Xóa các sản phẩm đã đặt hàng khỏi giỏ hàng
                cart_items.delete()
                
                # Xóa session data
                for key in ['selected_items', 'voucher_id', 'voucher_code', 'voucher_discount']:
                    if key in request.session:
                        del request.session[key]
                
                # Nếu thanh toán là PayPal, chuyển hướng đến trang thanh toán PayPal
                if payment_method == 'paypal':
                    # Lưu order_id vào session để xử lý sau khi thanh toán
                    request.session['order_id'] = order.id
                    
                    # Chuyển hướng đến view process_paypal để xử lý thanh toán
                    return redirect('process_paypal')
                else:
                    # Phương thức thanh toán khác (như COD), tiếp tục xử lý như hiện tại
                    messages.success(request, 'Đặt hàng thành công!')
                    return redirect('order_confirmation')
    
    # Chuẩn bị context cho template - giữ nguyên
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'user_addresses': user_addresses,
        'default_address': default_address,
        'applied_voucher': applied_voucher,
        'original_total': original_total,
        'discount_amount': discount_amount,
        'discount_value': discount_value
    }
    
    return render(request, 'home/checkout.html', context)
def order_confirmation(request):
    return render(request, 'home/order_confirmation.html')

def order_list(request):
    user = request.user
    status_filter = request.GET.get('status', 'all')
    
    # Lấy tất cả đơn hàng của user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Lọc theo trạng thái nếu có
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,   
        'current_status': status_filter,
    }
    
    return render(request, 'home/orders.html', context)


def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = order.items.all()
       
        context = {
            'order': order,
            'order_items': order_items,
        }
       
        return render(request, 'home/orderdetail.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Đơn hàng không tồn tại.')
        return redirect('order_list')
    
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Chỉ cho phép hủy đơn hàng ở trạng thái pending
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            messages.success(request, 'Đơn hàng #' + str(order_id) + ' đã được hủy thành công.')
        else:
            messages.error(request, 'Không thể hủy đơn hàng này vì đã được xử lý.')
            
        return redirect('order_detail', order_id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Đơn hàng không tồn tại.')
        return redirect('order_list')
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm

from django.core.cache import cache
import requests
from datetime import timedelta

import requests
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect

from decimal import Decimal
import logging
import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm

def get_exchange_rate():
    """
    Lấy tỷ giá VND sang USD với caching
    """
    try:
        # Sử dụng tỷ giá cố định để tránh các vấn đề với API
        return Decimal('0.000043')
    except Exception as e:
        print(f"Lỗi lấy tỷ giá: {e}")
        return Decimal('0.000043')

def process_paypal(request):
    """
    Xử lý thanh toán PayPal
    """
    try:
        # Log bắt đầu xử lý
        print("Bắt đầu xử lý PayPal")
        
        # Lấy order_id từ session
        order_id = request.session.get('order_id')
        if not order_id:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('home')
        
        print(f"Order ID: {order_id}")
        
        # Lấy thông tin đơn hàng
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, 'Đơn hàng không tồn tại')
            return redirect('home')
        
        # In thông tin đơn hàng để debug
        print(f"Tổng số tiền: {order.total_amount}")
        
        # Lấy tỷ giá
        exchange_rate = get_exchange_rate()
        print(f"Tỷ giá: {exchange_rate}")
        
        # Chuyển đổi VND sang USD
        try:
            usd_amount = float(round(order.total_amount * exchange_rate, 2))
            usd_amount = max(usd_amount, 0.01)
        except Exception as convert_error:
            print(f"Lỗi chuyển đổi tiền: {convert_error}")
            messages.error(request, 'Lỗi chuyển đổi tiền tệ')
            return redirect('home')
        
        print(f"Số tiền USD: {usd_amount}")
        
        # Địa chỉ host
        host = request.get_host()
        
        # Chuẩn bị thông tin thanh toán PayPal
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': str(usd_amount),  # Số tiền là USD
            'item_name': f'Đơn hàng #{order.id}',
            'invoice': str(order.id),
            'currency_code': 'USD',
            'notify_url': f'http://{host}{reverse("paypal-ipn")}',
            'return_url': f'http://{host}{reverse("payment_done")}',
            'cancel_return': f'http://{host}{reverse("payment_canceled")}',
        }
        
        # In thông tin PayPal để debug
        print("PayPal Dict:", paypal_dict)
        
        # Tạo form PayPal
        form = PayPalPaymentsForm(initial=paypal_dict)
        
        # Render template
        return render(request, 'home/payment_process.html', {
            'order': order, 
            'form': form,
            'usd_amount': usd_amount,
        })
    
    except Exception as e:
        # Ghi log toàn bộ lỗi
        print(f"Lỗi không xác định: {e}")
        messages.error(request, 'Có lỗi xảy ra khi xử lý thanh toán')
        return redirect('home')
def payment_done(request):
    # Lấy order_id từ session
    order_id = request.session.get('order_id')
    if order_id:
        try:
            # Cập nhật trạng thái thanh toán của đơn hàng
            order = Order.objects.get(id=order_id)
            order.payment_status = True
            order.save()
            
            # Xóa order_id khỏi session
            del request.session['order_id']
            
            messages.success(request, 'Thanh toán thành công!')
            return redirect('order_confirmation')
            
        except Order.DoesNotExist:
            pass
    
    return redirect('home')

def payment_canceled(request):
    # Xử lý khi người dùng hủy thanh toán
    messages.warning(request, 'Thanh toán đã bị hủy')
    return redirect('checkout')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, UserRating, Productvariant
from .forms import UserRatingForm

from django.contrib import messages  # Thêm import này

def rate_order_item(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    
    # Kiểm tra xem đơn hàng đã hoàn thành chưa
    if order_item.order.status != 'done':
        messages.error(request, 'Chỉ được đánh giá đơn hàng đã hoàn thành')
        return redirect('order_list')
    
    # Kiểm tra xem người đánh giá có phải chủ đơn hàng không
    if order_item.order.user != request.user:
        messages.error(request, 'Bạn không có quyền đánh giá đơn hàng này')
        return redirect('order_list')

    # Kiểm tra xem sản phẩm đã được đánh giá chưa
    existing_rating = UserRating.objects.filter(
        user=request.user,
        product_variant=order_item.product_variant,
        order=order_item.order
    ).first()

    if existing_rating:
        messages.warning(request, 'Sản phẩm này đã được đánh giá trong đơn hàng này')
        return redirect('order_list')
    
    if request.method == 'POST':
        form = UserRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.product_variant = order_item.product_variant
            rating.order = order_item.order
            rating.save()
            messages.success(request, 'Đánh giá của bạn đã được ghi nhận')
            return redirect('order_list')
    else:
        form = UserRatingForm()
    
    context = {
        'form': form,
        'order_item': order_item,
    }
    return render(request, 'home/rate_order_item.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, Feedback
from .forms import FeedbackForm

def create_feedback(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Kiểm tra xem đơn hàng đã được giao chưa
    if order.status != 'done':
        messages.error(request, 'Chỉ được phản hồi khi đơn hàng đã hoàn thành.')
        return redirect('order_list', order_id=order_id)
    
    # Kiểm tra xem đã tồn tại feedback chưa
    existing_feedback = Feedback.objects.filter(order=order).exists()
    if existing_feedback:
        messages.error(request, 'Bạn đã gửi phản hồi cho đơn hàng này rồi.')
        return redirect('order_list', order_id=order_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, user=request.user, order=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cảm ơn bạn đã gửi phản hồi!')
            return redirect('order_list')
    else:
        form = FeedbackForm(user=request.user, order=order)
    
    return render(request, 'home/feedback.html', {
        'form': form,
        'order': order
    })
    
from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category, Producttype, Productvariant

def danh_sach_san_pham(request):
    # Lấy các màu và size duy nhất từ variants
    colors = Productvariant.objects.values_list('color', flat=True).distinct()
    sizes = Productvariant.objects.values_list('size', flat=True).distinct()
    
    # Bắt đầu với tất cả sản phẩm
    products = Product.objects.prefetch_related('variants').select_related('id_discount_percentage').all()
    
    # Lấy các tham số lọc từ request
    category_id = request.GET.get('category')
    product_type_id = request.GET.get('product_type')
    color = request.GET.get('color')
    size = request.GET.get('size')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Debug: In ra các tham số filter
    print(f"Filtering with: category={category_id}, product_type={product_type_id}")
    
    # Lọc theo danh mục - Chỉ lọc khi category_id không phải là None hoặc chuỗi rỗng
    if category_id and category_id.strip():
        try:
            products = products.filter(type__category_id=int(category_id))
            print(f"Filtered products count after category filter: {products.count()}")
        except (ValueError, TypeError):
            # Nếu category_id không hợp lệ, giữ nguyên danh sách sản phẩm
            print("Invalid category ID")
    
    # Lọc theo loại sản phẩm
    if product_type_id and product_type_id.strip():
        products = products.filter(type_id=int(product_type_id))
    
    # Lọc theo màu
    if color and color.strip():
        products = products.filter(variants__color=color).distinct()
    
    # Lọc theo size
    if size and size.strip():
        products = products.filter(variants__size=size).distinct()
    
    # Lọc theo khoảng giá
    if min_price and max_price:
        products = products.filter(
            variants__price__range=(float(min_price), float(max_price))
        ).distinct()
    
    # Khởi tạo product_list để chứa thông tin sản phẩm
    product_list = []
    
    # Duyệt từng sản phẩm để thêm thông tin chi tiết
    for product in products:
        # Lấy variant đầu tiên của sản phẩm
        first_variant = product.variants.first()
        
        # Lấy hình ảnh của variant
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        # Tính toán giảm giá
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        
        product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam)
        }
        product_list.append(product_data)
    
    # Lấy danh sách các category và producttype để hiển thị sidebar
    categories = Category.objects.all()
    product_types = Producttype.objects.all()
    
    # Debug: In ra số lượng sản phẩm cuối cùng
    print(f"Final product list count: {len(product_list)}")
    
    try:
        ao_category = Category.objects.get(name='Áo')
        ao_category_id = ao_category.id
    except Category.DoesNotExist:
        ao_category_id = None

    try:
        quan_category = Category.objects.get(name='Quần')
        quan_category_id = quan_category.id
    except Category.DoesNotExist:
        quan_category_id = None

    try:
        vay_category = Category.objects.get(name='Váy')
        vay_category_id = vay_category.id
    except Category.DoesNotExist:
        vay_category_id = None

    context = {
        'products': products,
        'categories': categories,
        'product_types': product_types,
        'colors': colors,
        'sizes': sizes,
        'product_list': product_list,
        'ao_category_id': ao_category_id,
        'quan_category_id': quan_category_id,
        'vay_category_id': vay_category_id,
    }

    return render(request, 'home/danh_sach_san_pham.html', context)
# Trong hàm buy_now, bạn có thể thêm logic để:
def buy_now(request, variant_id):
    # Kiểm tra đăng nhập
    if not request.user.is_authenticated:
        messages.error(request, 'Vui lòng đăng nhập để thanh toán')
        return redirect('login')

    try:
        # Lấy variant được chọn
        variant = Productvariant.objects.get(id=variant_id)

        # Kiểm tra tồn kho
        if variant.stock < 1:
            messages.error(request, 'Sản phẩm đã hết hàng')
            return redirect('product_detail', product_id=variant.product.id)

        # Lấy user hiện tại
        user = UserClient.objects.get(username=request.user.username)

        # Tạo hoặc lấy giỏ hàng
        cart, created = Cart.objects.get_or_create(user_id=user)

        # Xóa các item cũ trong giỏ hàng (nếu muốn mua ngay chỉ có 1 sản phẩm)
        cart.items.all().delete()

        # Tạo cart item mới
        cart_item = CartItem.objects.create(
            cart_id=cart,
            product_variant_id=variant,
            quantity=1  # Mặc định là 1 sản phẩm
        )

        # Lưu ID của cart item vào session để chuyển thẳng đến checkout
        request.session['selected_items'] = [cart_item.id]

        # Chuyển hướng đến trang checkout
        return redirect('checkout')

    except Productvariant.DoesNotExist:
        messages.error(request, 'Không tìm thấy sản phẩm')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('home')
    
def search_products(request):
    # Lấy từ khóa tìm kiếm từ request
    search_query = request.GET.get('search', '').strip()
    
    # Nếu không có từ khóa tìm kiếm, trả về list rỗng
    if not search_query:
        return render(request, 'search/search_results.html', {
            'product_list': [],
            'search_query': search_query,
            'message': 'Vui lòng nhập từ khóa tìm kiếm'
        })
    
    # Tìm kiếm sản phẩm
    products = Product.objects.prefetch_related('variants').select_related('id_discount_percentage').filter(name__icontains=search_query)
    
    # Xử lý danh sách sản phẩm
    product_list = []
    
    for product in products:
        # Lấy hình ảnh của biến thể đầu tiên (nếu có)
        first_variant = product.variants.first()
        first_variant_image = first_variant.image.url if first_variant and first_variant.image else None
        
        # Tính toán giảm giá
        discount_percent = product.id_discount_percentage.percent if product.id_discount_percentage else 0
        giagoc = product.base_price
        giagiam = giagoc - (giagoc * discount_percent/100)
        
        # Tạo dictionary sản phẩm
        product_data = {
            'product': product,
            'variant_image': first_variant_image,
            'discount_percent': discount_percent,
            'giagoc': format_currency(giagoc),
            'giagiam': format_currency(giagiam)
        }
        
        product_list.append(product_data)
    
    # Render template kết quả tìm kiếm
    return render(request, 'home/search_results.html', {
        'product_list': product_list,
        'search_query': search_query,
        'message': f'Tìm thấy {len(product_list)} sản phẩm' if product_list else 'Không tìm thấy sản phẩm nào'
    })