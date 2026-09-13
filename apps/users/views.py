from django.contrib.auth import get_user_model
from drf_spectacular.views import extend_schema
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    RegisterSerializer,
    TopUpBalanceSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    pagination_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class TopUpBalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=TopUpBalanceSerializer, responses=UserProfileSerializer)
    def post(self, request):
        serializer = TopUpBalanceSerializer(instance=request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)
