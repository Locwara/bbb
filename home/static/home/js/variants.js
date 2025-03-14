
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
        const mainImage = document.getElementById('main-image');
        mainImage.style.animation = 'none';
        mainImage.offsetHeight; // Trigger reflow
        mainImage.style.animation = 'fadeIn 0.5s';
        
        // Cập nhật hình ảnh sản phẩm
        mainImage.src = variantsData[color].image;
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
            document.getElementById('size-options').style.borderRadius='12px';
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
        
        // Thêm lớp để kích hoạt hiệu ứng fade-out
        priceElement.classList.add('fade-out');
        stockElement.classList.add('fade-out');
        
        // Đợi animation fade-out hoàn tất rồi mới cập nhật nội dung
        setTimeout(() => {
            if (selectedColor && selectedSize) {
                currentVariant = variantsData[selectedColor].sizes.find(s => s.size === selectedSize);
                if (currentVariant) {
                    priceElement.textContent = `Giá: ${formatPrice(currentVariant.price)}`;
                    stockElement.textContent = `Còn lại: ${currentVariant.stock} sản phẩm`;
                    addToCartButton.disabled = currentVariant.stock === 0;
                    
                    // Thêm hiệu ứng cho nút khi được kích hoạt
                    if (currentVariant.stock > 0) {
                        addToCartButton.classList.add('button-active');
                    } else {
                        addToCartButton.classList.remove('button-active');
                    }
                }
            } else {
                currentVariant = null;
                priceElement.textContent = '';
                stockElement.textContent = '';
                addToCartButton.disabled = true;
                addToCartButton.classList.remove('button-active');
            }
            
            // Xóa lớp fade-out và thêm lớp fade-in
            priceElement.classList.remove('fade-out');
            stockElement.classList.remove('fade-out');
            priceElement.classList.add('fade-in');
            stockElement.classList.add('fade-in');
            
            // Xóa lớp fade-in sau khi animation hoàn tất
            setTimeout(() => {
                priceElement.classList.remove('fade-in');
                stockElement.classList.remove('fade-in');
            }, 500);
        }, 150);
    }
    
    function updateVariantInfo() {
        const variantInfoElement = document.getElementById('variant-info');
        
        // Thêm lớp để kích hoạt hiệu ứng fade-out
        variantInfoElement.classList.add('fade-out');
        
        // Đợi animation fade-out hoàn tất rồi mới cập nhật nội dung
        setTimeout(() => {
            if (selectedColor && selectedSize && currentVariant) {
                variantInfoElement.innerHTML = `
                    <strong>Sản phẩm đã chọn:</strong><br>
                    <div class="color-option1" style="background-color: ${selectedColor}"></div><br>
                    Size: ${selectedSize}<br>
                    Còn lại: ${currentVariant.stock} sản phẩm
                `;
            } else {
                variantInfoElement.innerHTML = 'Vui lòng chọn màu sắc và kích thước';
            }
            
            // Xóa lớp fade-out và thêm lớp fade-in
            variantInfoElement.classList.remove('fade-out');
            variantInfoElement.classList.add('fade-in');
            
            // Xóa lớp fade-in sau khi animation hoàn tất
            setTimeout(() => {
                variantInfoElement.classList.remove('fade-in');
            }, 500);
        }, 200);
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
        
        // Thêm lớp để kích hoạt hiệu ứng fade-out
        unitPriceElement.classList.add('price-fade-out');
        quantityDisplayElement.classList.add('price-fade-out');
        totalPriceElement.classList.add('price-fade-out');
        
        // Đợi animation fade-out hoàn tất rồi mới cập nhật nội dung
        setTimeout(() => {
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
            
            // Xóa lớp fade-out và thêm lớp fade-in
            unitPriceElement.classList.remove('price-fade-out');
            quantityDisplayElement.classList.remove('price-fade-out');
            totalPriceElement.classList.remove('price-fade-out');
            
            unitPriceElement.classList.add('price-fade-in');
            quantityDisplayElement.classList.add('price-fade-in');
            totalPriceElement.classList.add('price-fade-in');
            
            // Xóa lớp fade-in sau khi animation hoàn tất
            setTimeout(() => {
                unitPriceElement.classList.remove('price-fade-in');
                quantityDisplayElement.classList.remove('price-fade-in');
                totalPriceElement.classList.remove('price-fade-in');
            }, 500);
        }, 100);
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
