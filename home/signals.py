from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from home.models import Order
@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn_obj = sender
    
    if ipn_obj.payment_status == 'Completed':
        # Thanh toán đã được xác nhận
        try:
            # Tìm đơn hàng dựa trên invoice number
            order = Order.objects.get(id=ipn_obj.invoice)
            # Cập nhật trạng thái thanh toán
            order.payment_status = True
            order.save()
        except Order.DoesNotExist:
            pass