from django.contrib.auth.views import LogoutView
from django.urls import path

from api.views import (ProductDetailView, LoginView, ReviewCreateView, UserCreateView, CatalogListView,
                       AvatarUpdateView, PasswordUpdateView, ProfileView)

app_name = "api"

urlpatterns = [
    path("product/<int:pk>", ProductDetailView.as_view(), name="product_details"),
    path("product/<int:product_id>/reviews", ReviewCreateView.as_view(), name="review_create"),
    path("catalog/", CatalogListView.as_view(), name="catalog"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("profile/avatar", AvatarUpdateView.as_view(), name="avatar"),
    path("profile/password", PasswordUpdateView.as_view(), name="password"),
    path("sign-in", LoginView.as_view(), name="login"),
    path("sign-up", UserCreateView.as_view(), name="register"),
    path("sign-out", LogoutView.as_view(), name="logout"),
]