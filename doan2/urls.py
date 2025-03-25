"""
URL configuration for doan2 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from home import views as home
from django.views.generic.base import RedirectView
urlpatterns = [
    # include tới urls.py của home
    path('login-client/', include("home.urls")),
    # url cho phần login google dùng để trả về trang chủ sau khi login thành công
    path('accounts/google/login/callback/', home.google_callback, name='google_callback'),
    path('',RedirectView.as_view(url='login-client/home/', permanent=False), name='index'),
    path('social-auth/', include('social_django.urls', namespace='social'), name='socialf'),
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('payment-done/', home.payment_done, name='payment_done'),
    path('payment-canceled/', home.payment_canceled, name='payment_canceled'),      

]
# Chỉ thêm cấu hình phục vụ media khi đang trong môi trường phát triển
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)