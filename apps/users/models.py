from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Баланс пользователя, используемый для покупок",
    )

    def __str__(self):
        return self.username
