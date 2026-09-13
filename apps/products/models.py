from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    stock = models.PositiveBigIntegerField(default=0, help_text="Кол-во на складе")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0
