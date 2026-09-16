from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)

    return cart


class CartDetailView(generics.RetrieveAPIView):
    """Показывает корзину пользователи, содержимое и их цены."""

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_or_create_cart(self.request.user)


class CartItemAddView(generics.CreateAPIView):
    """Добавляет продукт в корзину."""

    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_or_create_cart(request.user)
        product = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))
        existing = CartItem.objects.filter(cart=cart, product_id=product).first()

        if existing:
            data = {"product_id": product, "quantity": existing.quantity + quantity}
            serializer = self.get_serializer(existing, data=data)
        else:
            serializer = self.get_serializer(
                data={"product_id": product, "quantity": quantity}
            )

        serializer.is_valid(raise_exception=True)
        serializer.save(cart=cart)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """Обновляет кол-во товаров (PATCH) или удаляет (DELETE) один товар из корзины."""

    permission_classes = [permissions.IsAuthenticated]

    def get_item(self, request, item_id):
        cart = get_or_create_cart(request.user)

        return generics.get_object_or_404(CartItem, cart=cart, id=item_id)

    def patch(self, request, item_id):
        item = self.get_item(request, item_id)
        serializer = CartItemSerializer(item, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, item_id):
        item = self.get_item(request, item_id)
        item.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
