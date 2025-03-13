document.addEventListener('DOMContentLoaded', function() {
    // Lấy tất cả các phần tử sản phẩm
    const products = document.querySelectorAll('.sp');
    
    // Thêm event listener cho mỗi sản phẩm
    products.forEach(product => {
        // Hiệu ứng khi hover vào
        product.addEventListener('mouseenter', function() {
            // Dùng GSAP hoặc có thể dùng animate API native
            this.style.transition = 'all 0.3s ease';
            this.style.transform = 'scale(1.08) translateZ(20px)';
            this.style.zIndex = '10';
            this.style.boxShadow = '0 10px 20px rgba(0,0,0,0.2)';
            
            // Hiệu ứng cho hình ảnh
            const img = this.querySelector('.chuaanh img');
            if (img) {
                img.style.transition = 'all 0.4s ease';
                img.style.transform = 'scale(1.1)';
            }
            
            // Hiệu ứng cho tên sản phẩm
            const tensp = this.querySelector('.tensp');
            if (tensp) {
                tensp.style.color = '#ff6b6b';
                tensp.style.fontWeight = 'bold';
            }
            
            // Hiệu ứng cho phần trăm giảm giá
            const ptg = this.querySelector('.ptg');
            if (ptg) {
                ptg.style.transition = 'all 0.3s ease';
                ptg.style.transform = 'scale(1.1) rotate(-3deg)';
            }
        });
        
        // Hiệu ứng khi rời chuột
        product.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) translateZ(0)';
            this.style.zIndex = '1';
            this.style.boxShadow = 'none';
            
            // Đặt lại hình ảnh
            const img = this.querySelector('.chuaanh img');
            if (img) {
                img.style.transform = 'scale(1)';
            }
            
            // Đặt lại tên sản phẩm
            const tensp = this.querySelector('.tensp');
            if (tensp) {
                tensp.style.color = '';
                tensp.style.fontWeight = '';
            }
            
            // Đặt lại phần trăm giảm giá
            const ptg = this.querySelector('.ptg');
            if (ptg) {
                ptg.style.transform = 'scale(1) rotate(0)';
            }
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    let currentSlide = 0;
    let slideInterval;
    
    // Hàm hiển thị slide
    function showSlide(n) {
        // Xóa class active cho tất cả slide và dots
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        // Reset về slide đầu tiên nếu vượt quá số lượng
        if (n >= slides.length) {
            currentSlide = 0;
        } else if (n < 0) {
            currentSlide = slides.length - 1;
        } else {
            currentSlide = n;
        }
        
        // Thêm class active cho slide hiện tại và dot tương ứng
        slides[currentSlide].classList.add('active');
        dots[currentSlide].classList.add('active');
    }
    
    // Hàm chuyển slide tiếp theo
    function nextSlide() {
        showSlide(currentSlide + 1);
    }
    
    // Hàm chuyển slide trước đó
    function prevSlide() {
        showSlide(currentSlide - 1);
    }
    
    // Thiết lập chuyển slide tự động
    function startSlideInterval() {
        slideInterval = setInterval(nextSlide, 5000);
    }
    
    // Dừng chuyển slide tự động
    function stopSlideInterval() {
        clearInterval(slideInterval);
    }
    
    // Sự kiện click nút next
    nextBtn.addEventListener('click', function() {
        stopSlideInterval();
        nextSlide();
        startSlideInterval();
    });
    
    // Sự kiện click nút prev
    prevBtn.addEventListener('click', function() {
        stopSlideInterval();
        prevSlide();
        startSlideInterval();
    });
    
    // Sự kiện click dots
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
            stopSlideInterval();
            const slideIndex = parseInt(dot.getAttribute('data-index'));
            showSlide(slideIndex);
            startSlideInterval();
        });
    });
    
    // Bắt đầu chuyển slide tự động
    startSlideInterval();
});