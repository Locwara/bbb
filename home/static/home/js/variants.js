
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Hàm cập nhật hiển thị số lượng sản phẩm trong giỏ hàng (nếu có)
    function updateCartCount(count) {
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = count;
        }
    }
    
    
    let selectedColor = null;
    let selectedSize = null;
    let currentVariant = null;
    
    document.addEventListener('DOMContentLoaded', function() {
        // Tự động chọn màu sắc đầu tiên khi trang được tải
        const firstColor = Object.keys(variantsData)[0];
        selectColor(firstColor);
        
        // Thêm sự kiện click cho các tùy chọn màu sắc
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.addEventListener('click', function() {
                selectColor(this.dataset.color);
            });
        });
    });
    
    function selectColor(color) {
        selectedColor = color;
        selectedSize = null;
        currentVariant = null;
        
        // Cập nhật trạng thái active cho tùy chọn màu
        document.querySelectorAll('.color-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.color === color);
        });
        
        // Cập nhật hình ảnh sản phẩm - Sử dụng đường dẫn đầy đủ
        document.getElementById('main-image').src = variantsData[color].image;
        
        // Cập nhật các tùy chọn kích thước
        updateSizeOptions(color);
        updateProductInfo();
        resetQuantity();
        updateVariantInfo();
        updatePriceInfo();
    }
    
    function updateSizeOptions(color) {
        const sizeOptionsContainer = document.getElementById('size-options');
        const sizes = variantsData[color].sizes;
        
        sizeOptionsContainer.innerHTML = sizes.map(size => `
            <div class="size-option" 
                 data-size="${size.size}"
                 onclick="selectSize('${size.size}')">
                ${size.size}
            </div>
        `).join('');
    }
    
    function selectSize(size) {
        selectedSize = size;
        
        // Cập nhật trạng thái active cho tùy chọn kích thước
        document.querySelectorAll('.size-option').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.size === size);
        });
        
        updateProductInfo();
        resetQuantity();
        updateVariantInfo();
        updatePriceInfo();
    }
    
    function updateProductInfo() {
        const priceElement = document.getElementById('price');
        const stockElement = document.getElementById('stock');
        const addToCartButton = document.getElementById('add-to-cart');
        
        if (selectedColor && selectedSize) {
            currentVariant = variantsData[selectedColor].sizes.find(s => s.size === selectedSize);
            if (currentVariant) {
                priceElement.textContent = `Giá: ${formatPrice(currentVariant.price)}`;
                stockElement.textContent = `Còn lại: ${currentVariant.stock} sản phẩm`;
                addToCartButton.disabled = currentVariant.stock === 0;
            }
        } else {
            currentVariant = null;
            priceElement.textContent = '';
            stockElement.textContent = '';
            addToCartButton.disabled = true;
        }
    }
    
    function updateVariantInfo() {
        const variantInfoElement = document.getElementById('variant-info');
        if (selectedColor && selectedSize && currentVariant) {
            variantInfoElement.innerHTML = `
                <strong>Sản phẩm đã chọn:</strong><br>
                Màu: ${selectedColor}<br>
                Size: ${selectedSize}<br>
                Còn lại: ${currentVariant.stock} sản phẩm
            `;
        } else {
            variantInfoElement.innerHTML = 'Vui lòng chọn màu sắc và kích thước';
        }
    }
    
    function validateQuantity() {
        const quantityInput = document.getElementById('quantity');
        let quantity = parseInt(quantityInput.value);
        
        if (isNaN(quantity) || quantity < 1) {
            quantity = 1;
        }
        
        if (currentVariant && quantity > currentVariant.stock) {
            quantity = currentVariant.stock;
        }
        
        quantityInput.value = quantity;
        updatePriceInfo();
    }
    
    function increaseQuantity() {
        const quantityInput = document.getElementById('quantity');
        let quantity = parseInt(quantityInput.value);
        
        if (currentVariant && quantity < currentVariant.stock) {
            quantityInput.value = quantity + 1;
            updatePriceInfo();
        }
    }
    
    function decreaseQuantity() {
        const quantityInput = document.getElementById('quantity');
        let quantity = parseInt(quantityInput.value);
        
        if (quantity > 1) {
            quantityInput.value = quantity - 1;
            updatePriceInfo();
        }
    }
    
    function resetQuantity() {
        document.getElementById('quantity').value = 1;
        updatePriceInfo();
    }
    
    function formatPrice(price) {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
    }
    
    function updatePriceInfo() {
        const unitPriceElement = document.getElementById('unit-price');
        const quantityDisplayElement = document.getElementById('quantity-display');
        const totalPriceElement = document.getElementById('total-price');
        const quantity = parseInt(document.getElementById('quantity').value);
    
        if (currentVariant) {
            const unitPrice = parseFloat(currentVariant.price);
            const totalPrice = unitPrice * quantity;
    
            unitPriceElement.textContent = formatPrice(unitPrice);
            quantityDisplayElement.textContent = quantity;
            totalPriceElement.textContent = formatPrice(totalPrice);
        } else {
            unitPriceElement.textContent = '0đ';
            quantityDisplayElement.textContent = '0';
            totalPriceElement.textContent = '0đ';
        }
    }
    function addToCart() {
        if (!selectedColor || !selectedSize || !currentVariant) {
            alert('Vui lòng chọn màu sắc và kích thước');
            return;
        }
        
        const quantity = parseInt(document.getElementById('quantity').value);
        if (isNaN(quantity) || quantity < 1) {
            alert('Số lượng không hợp lệ');
            return;
        }
        
        // Tìm variant_id từ dữ liệu variant hiện tại
        const variantId = currentVariant.id; // Đảm bảo biến currentVariant có chứa id
        
        // Gửi request đến server
        fetch(addToCartUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Hàm lấy CSRF token
            },
            body: JSON.stringify({
                variant_id: variantId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                // Cập nhật số lượng sản phẩm trong giỏ hàng ở header (nếu có)
                updateCartCount(data.cart_count);
            } else {
                alert(data.message || 'Có lỗi xảy ra khi thêm vào giỏ hàng');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Có lỗi xảy ra khi thêm vào giỏ hàng: ' + error.message);
        });
    }
