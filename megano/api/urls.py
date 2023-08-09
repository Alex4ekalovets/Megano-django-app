from django.contrib.auth.views import LogoutView
from django.urls import path

from api.views import (ProductDetailView, SignInView, ReviewCreateView, SignUpView, CatalogListView,
                       AvatarUpdateView, PasswordUpdateView, ProfileView, TagListView, CategoryListView)

app_name = "api"

urlpatterns = [
    # auth
    path("sign-in", SignInView.as_view(), name="sign-in"),
    path("sign-up", SignUpView.as_view(), name="sign-up"),
    path("sign-out", LogoutView.as_view(), name="sign-out"),

    # catalog
    path("categories", CategoryListView.as_view(), name="categories"),
    path("catalog", CatalogListView.as_view(), name="catalog"),
    # path("products/popular", , name="popular_products"),
    # path("products/limited", , name="limited_products"),
    # path("sales", , name="sales"),
    # path("banners", , name="banners"),

    # basket
    # path("basket", , name="basket"),

    # order
    # path("orders", , name="orders"),
    # path("orders/<int:pk>", , name="order_details"),

    # payment
    # path("payment", , name="payment"),

    # profile
    path("profile", ProfileView.as_view(), name="profile"),
    path("profile/avatar", AvatarUpdateView.as_view(), name="avatar"),
    path("profile/password", PasswordUpdateView.as_view(), name="password"),

    # tags
    path("tags", TagListView.as_view(), name="tags"),

    # product
    path("product/<int:pk>", ProductDetailView.as_view(), name="product_details"),
    path("product/<int:product_id>/reviews", ReviewCreateView.as_view(), name="review_create"),
]