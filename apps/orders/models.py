from django.conf import settings
from django.db import models

from apps.products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "ожидание", "Ожидание"
        COMPLETED = "завершен", "Завершен"
        CANCELLED = "отменен", "Отменен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.COMPLETED
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ #{self.id} пользователя {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, help_text="Куплено по цене"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity
