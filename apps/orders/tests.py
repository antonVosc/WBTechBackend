from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.cart.models import Cart, CartItem
from apps.products.models import Product
from .models import Order
from .services import OrderCreationError, create_order_from_cart

User = get_user_model()


class CreateOrderFromCartServiceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Роман", password="pass12345", balance=Decimal("100.00")
        )
        self.product = Product.objects.create(
            name="Клавиатура", price=Decimal("30.00"), stock=5
        )
        self.cart = Cart.objects.create(user=self.user)
        
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_successful_checkout_deducts_balance_and_stock(self):
        order = create_order_from_cart(self.user)

        self.user.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(order.total_price, Decimal("60.00"))
        self.assertEqual(self.user.balance, Decimal("40.00"))
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_fails_on_insufficient_balance(self):
        self.user.balance = Decimal("10.00")
        self.user.save()
        
        with self.assertRaises(OrderCreationError):
            create_order_from_cart(self.user)
        
        self.assertEqual(self.cart.items.count(), 1)

    def test_checkout_fails_on_insufficient_stock(self):
        CartItem.objects.filter(cart=self.cart, product=self.product).update(
            quantity=999
        )
        
        with self.assertRaises(OrderCreationError):
            create_order_from_cart(self.user)

    def test_checkout_fails_on_empty_cart(self):
        self.cart.items.all().delete()
        
        with self.assertRaises(OrderCreationError):
            create_order_from_cart(self.user)


class OrderApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="Виктор", password="pass12345", balance=Decimal("50.00")
        )
        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(
            name="Мышка", price=Decimal("10.00"), stock=10
        )
        self.cart = Cart.objects.create(user=self.user)
        
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)

    def test_checkout_endpoint_creates_order(self):
        response = self.client.post(reverse("order-checkout"))
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)

    def test_checkout_endpoint_rejects_insufficient_balance(self):
        self.user.balance = Decimal("1.00")
        self.user.save()
        
        response = self.client.post(reverse("order-checkout"))
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_list_returns_only_own_orders(self):
        other = User.objects.create_user(username="Влад", password="pass12345")
        Order.objects.create(user=other, total_price=Decimal("5.00"))
        self.client.post(reverse("order-checkout"))
        
        response = self.client.get(reverse("order-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
