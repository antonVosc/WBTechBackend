import logging
from django.core.mail import send_mail

logger = logging.getLogger("orders")


def notify_order_created(order):
    message = (
        f"Order #{order.id} placed by '{order.user.username}' for "
        f"{order.total_price} — {order.items.count()} item(s)."
    )

    logger.info(message)

    if order.user.email:
        send_mail(
            subject=f"Order #{order.id} confirmed",
            message=message,
            from_email=None,
            recipient_list=[order.user.email],
            fail_silently=True,
        )
