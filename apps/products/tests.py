from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product

User = get_user_model()


class ProductPermissionsTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Книга", price=Decimal("9.99"), stock=5
        )
        self.admin = User.objects.create_user(
            username="admin", password="newuse21", is_staff=True
        )
        self.regular = User.objects.create_user(username="user", password="newuse21")

    def test_anyone_can_list_products(self):
        response = self.client.get(reverse("product-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create_product(self):
        response = self.client.get(
            reverse("product-list"), {"name": "X", "price": "1.00", "stock": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_product(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get(
            reverse("product-list"), {"name": "X", "price": "1.00", "stock": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_product(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            reverse("product-list"), {"name": "X", "price": "1.00", "stock": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_delete_product(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(reverse("product-detail", args=[self.product.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
