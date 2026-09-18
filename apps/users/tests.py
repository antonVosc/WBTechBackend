from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterTests(APITestCase):
    def test_registes_creates_user(self):
        url = reverse("user-register")
        payload = {
            "username": "Антон",
            "email": "av@yandex.ru",
            "password": "newpassw1234",
        }
        response = self.client.post(url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="Антон").exists())

        user = User.objects.get(username="Антон")
        self.assertTrue(user.check_password("newpassw1234"))


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Екатерина", password="newuse21")

        self.client.force_authenticate(user=self.user)

    def test_profile_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("user-profile"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_returns_current_user(self):
        response = self.client.get(reverse("user-profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "Екатерина")

    def test_top_up_balance(self):
        response = self.client.post(reverse("user-top-up"), {"amount": "100.00"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("100.00"))

    def test_top_up_rejects_non_positive_amount(self):
        response = self.client.post(reverse("user-top-up"), {"amount": "0"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
