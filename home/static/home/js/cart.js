$(document).ready(function () {
    let cartItems = $('.cart-items');

    // Kiểm tra xem phần tử .cart-items có tồn tại không
    if (cartItems.length > 0) {
        cartItems.scroll(function () {
            if (cartItems.scrollTop() > 0 || cartItems.scrollLeft() > 0) {
                cartItems.addClass('scrolled');
            } else {
                cartItems.removeClass('scrolled');
            }
        });
    }
});

function formatCurrency(amount) {
    // Chuyển số thành chuỗi và thêm dấu chấm ngăn cách hàng nghìn
    const formattedAmount = amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    
    // Thêm ký hiệu đơn vị tiền tệ
    return formattedAmount + " đ";
  }
  
// xử lý phần scrip cho tăng giảm số lượng sản phẩm trong giỏ hàng
// nút cộng trừ là .btn-quantity và hiển thị số lượng sản phẩm là .so 
$(document).ready(function () {
    $('.btn-quantity').click(function () {
        let $button = $(this);
        let oldValue = $button.parent().find('.so').val();
        let newVal;
        if ($button.text() == "+") {
            newVal = parseFloat(oldValue) + 1;
        } else {
            if (oldValue > 1) {
                newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 1;
            }
        }
        $button.parent().find('.so').val(newVal);
    });
});

document.addEventListener('DOMContentLoaded', function () {
    // Lấy tất cả các phần tử có class 'color-display'
    const colorDisplays = document.querySelectorAll('.color-display');

    // Duyệt qua từng phần tử
    colorDisplays.forEach(function (colorDisplay) {
        // Lấy giá trị màu từ nội dung của phần tử
        const color = colorDisplay.textContent.trim().toLowerCase();

        // Đặt màu nền cho hình tròn
        colorDisplay.style.backgroundColor = color;

        // Ẩn text màu (nếu bạn muốn)
        colorDisplay.textContent = '';
    });
});


$(document).ready(function() {
    // Tính tổng tiền khi checkbox thay đổi
    $('.check-box').change(function() {
        let total = 0;
        
        $('.check-box:checked').each(function() {
            const itemTotal = $(this).closest('.cart-item').find('.total').text();
            total += parseFloat(itemTotal.replace(/[^\d.]/g, '')) || 0;
        });

        $('.tongtien').text(total.toLocaleString('vi-VN') + '₫');
    });

    // Xử lý nút thanh toán
    $('.checkout-btn').click(function() {
        const selectedItems = [];
        
        // Lấy ID trực tiếp từ phần tử cart-item
        $('.check-box:checked').each(function() {
            // Đầu tiên, thử lấy ID từ data attribute nếu bạn đã thêm vào HTML
            const cartItem = $(this).closest('.cart-item');
            
            // Kiểm tra xem có form và action không
            const form = cartItem.find('form');
            if (form.length > 0 && form.attr('action')) {
                // Trích xuất ID từ URL action của form
                const actionUrl = form.attr('action');
                const matches = actionUrl.match(/\/(\d+)(?:\/)?$/);
                
                if (matches && matches[1]) {
                    selectedItems.push(parseInt(matches[1]));
                }
            }
        });

        console.log("Selected Items:", selectedItems); // Kiểm tra ID được chọn
        
        if(selectedItems.length === 0) {
            alert('Vui lòng chọn ít nhất 1 sản phẩm!');
            return;
        }

        // Tạo một form ẩn và gửi dữ liệu đến Django
        const form = $('<form></form>').attr({
            method: 'POST',
            action: '/login-client/checkout/'
        });
        
        // Thêm CSRF token
        form.append($('<input>').attr({
            type: 'hidden',
            name: 'csrfmiddlewaretoken',
            value: $('[name=csrfmiddlewaretoken]').val()
        }));
        
        // Thêm danh sách sản phẩm
        form.append($('<input>').attr({
            type: 'hidden',
            name: 'selected_items',
            value: JSON.stringify(selectedItems)
        }));
        
        $('body').append(form);
        form.submit();
    });
});