from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "balance", "date_joined")
        read_only_fields = ("id", "username", "balance", "date_joined")


class TopUpBalanceSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    def update(self, instance, validated_data):
        instance.balance += validated_data["amount"]
        instance.save(update_fields=["balance"])

        return instance
