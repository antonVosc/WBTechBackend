from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
from .services import OrderCreationError, create_order_from_cart


class OrderListView(generics.ListAPIView):
    """История заказов пользователя"""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderCreateView(APIView):
    """Создание товаров из корзины пользователя для оплаты"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            order = create_order_from_cart(request.user)
        except OrderCreationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
