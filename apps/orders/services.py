from django.db import transaction
from apps.cart.models import Cart
from apps.products.models import Product
from .models import Order, OrderItem
from .notifications import notify_order_created
from django.contrib.auth import get_user_model


class OrderCreationError(Exception):
    pass


@transaction.atomic
def create_order_from_cart(user):
    try:
        cart = Cart.objects.select_related("user").get(user=user)
    except Cart.DoesNotExist:
        raise OrderCreationError("Корзины не существует.")

    items = list(cart.items.select_related("product"))

    if not items:
        raise OrderCreationError("Корзина пуста.")

    product_ids = [item.product_id for item in items]
    products = {
        p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
    }
    total_price = 0

    for item in items:
        product = products[item.product_id]

        if item.quantity > product.stock:
            raise OrderCreationError(
                f"Нет места на складе для '{product.name}': "
                f"Нужно {item.quantity}, свободно {product.stock}."
            )

        total_price += product.price * item.quantity

    User = get_user_model()

    locked_user = User.objects.select_for_update().get(pk=user.pk)

    if locked_user.balance < total_price:
        raise OrderCreationError(
            f"Недостаточно баланса: нужно {total_price}, сейчас {locked_user.balance}."
        )

    order = Order.objects.create(user=locked_user, total_price=total_price)

    for item in items:
        product = products[item.product_id]

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=item.quantity,
        )

        product.stock -= item.quantity

        product.save(update_fields=["stock"])

    locked_user.balance -= total_price

    locked_user.save(update_fields=["balance"])

    cart.items.all().delete()
    notify_order_created(order)

    return order
