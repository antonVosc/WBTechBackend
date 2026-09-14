from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Product
from .permissions import IsAdminOrReadOnly
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    Каталог продуктов

    - GET /api/products/ и /api/products/{id}/ доступны всем
    - POST/DELETE/PUT/PATCH доступен только админам
    """

    queryset = Product.objects.all()

    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["price"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "stock"]
