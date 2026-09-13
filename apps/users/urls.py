from django.urls import path

from .views import ProfileView, RegisterView, TopUpBalanceView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user-register"),
    path("me/", ProfileView.as_view(), name="user-profile"),
    path("me/top-up/", TopUpBalanceView.as_view(), name="user-top-up"),
]
