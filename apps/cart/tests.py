from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.products.models import Product
from .models import Cart, CartItem

User = get_user_model()


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="carter", password="pass12345")
        self.client.force_authenticate(user=self.user)

        self.product = Product.objects.create(
            name="Мышка", price=Decimal("20.00"), stock=10
        )

    def test_view_empty_cart(self):
        response = self.client.get(reverse("cart-detail"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["items"], [])

    def test_add_item_to_cart(self):
        response = self.client.post(
            reverse("cart-item-add"), {"product_id": self.product.id, "quantity": 2}
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        cart = Cart.objects.get(user=self.user)
        
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_cannot_add_more_than_stock(self):
        response = self.client.post(
            reverse("cart-item-add"), {"product_id": self.product.id, "quantity": 999}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_quantity(self):
        item = CartItem.objects.create(
            cart=Cart.objects.create(user=self.user), product=self.product, quantity=1
        )
        response = self.client.patch(
            reverse("cart-item-detail", args=[item.id]), {"quantity": 3}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        item.refresh_from_db()
        self.assertEqual(item.quantity, 3)

    def test_remove_item(self):
        item = CartItem.objects.create(
            cart=Cart.objects.create(user=self.user), product=self.product, quantity=1
        )
        response = self.client.delete(reverse("cart-item-detail", args=[item.id]))
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())
