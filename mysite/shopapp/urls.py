from django.contrib.auth.views import LogoutView
from django.urls import path

from shopapp.views import ProductDetailView, LoginView, ReviewCreateView, UserCreateView, CatalogListView

app_name = "shopapp"

urlpatterns = [
    path("product/<int:pk>", ProductDetailView.as_view(), name="product_details"),
    path("product/<int:product_id>/reviews", ReviewCreateView.as_view(), name="review_create"),
    path("catalog/", CatalogListView.as_view(), name="catalog"),
    path("sign-in", LoginView.as_view(), name="login"),
    path("sign-up", UserCreateView.as_view(), name="register"),
    path("sign-out", LogoutView.as_view(), name="logout"),
]