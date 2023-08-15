import json
import random
from math import ceil

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Lower
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.viewsets import ModelViewSet

from api.models import (
    Category,
    Product,
    Profile,
    ProfileAvatar,
    Review,
    Sale,
    Tag,
    Basket,
    BasketItem,
    Order,
    OrderItem,
)
from api.serializers import (
    CatalogSerializer,
    CategorySerializer,
    LoginSerializer,
    PasswordSerializer,
    ProductSerializer,
    ProfileSerializer,
    ReviewSerializer,
    SaleSerializer,
    TagSerializer,
    UserSerializer,
    BasketSerializer,
    OrderSerializer,
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Avg, Count, F, Sum, Prefetch, BigAutoField
from rest_framework import pagination, status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CustomPagination(pagination.PageNumberPagination):
    page_query_param = "currentPage"
    page_size = 20

    def get_paginated_response(self, data):
        last_page = ceil(self.page.paginator.count / self.page_size)
        return Response(
            {
                "items": data,
                "currentPage": self.page.number,
                "lastPage": last_page,
            }
        )


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.annotate(rating=Avg("reviews__rate")).prefetch_related(
        "tags"
    )
    serializer_class = ProductSerializer


class PopularProductsListView(ListAPIView):
    queryset = (
        Product.objects.annotate(
            rating=Avg("reviews__rate"), reviews_count=Count("reviews")
        )
        .prefetch_related("tags")
        .order_by("-rating")[:8]
    )
    serializer_class = CatalogSerializer
    pagination_class = None


class LimitedProductsListView(ListAPIView):
    queryset = (
        Product.objects.annotate(
            rating=Avg("reviews__rate"), reviews_count=Count("reviews")
        )
        .prefetch_related("tags")
        .filter(limited_edition=True)
    )
    serializer_class = CatalogSerializer
    pagination_class = None


class BannerListView(ListAPIView):
    serializer_class = CatalogSerializer
    pagination_class = None

    def get_queryset(self):
        product_ids = list(Product.objects.values_list("id", flat=True))
        random_product_ids = random.sample(product_ids, min(len(product_ids), 3))
        queryset = (
            Product.objects.annotate(
                rating=Avg("reviews__rate"), reviews_count=Count("reviews")
            )
            .filter(id__in=random_product_ids)
            .prefetch_related("specifications", "images", "tags")
        )
        return queryset


class CatalogListView(ListAPIView):
    serializer_class = CatalogSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Product.objects.annotate(
            rating=Avg("reviews__rate"), reviews_count=Count("reviews")
        ).prefetch_related("specifications", "tags", "images")

        query_params = self.request.query_params

        categories = []

        def get_all_subcategories(category):
            categories.append(category.id)
            children = category.get_children()
            if children is None:
                return
            list(map(get_all_subcategories, children))

        if query_params.get("category") is not None:
            category = Category.objects.get(id=int(query_params.get("category")))
            get_all_subcategories(category)
            queryset = queryset.filter(category__in=categories)
        if query_params.get("tags[]") is not None:
            queryset = queryset.filter(
                tags__in=map(int, query_params.getlist("tags[]"))
            )
        if query_params.get("filter[freeDelivery]") == "true":
            queryset = queryset.filter(freeDelivery=True)
        if query_params.get("filter[available]") == "true":
            queryset = queryset.exclude(count=0)
        if query_params.get("sortType") == "dec":
            sort = "-" + query_params.get("sort")
        else:
            sort = query_params.get("sort")

        queryset = queryset.filter(
            title__icontains=query_params.get("filter[name]"),
            price__range=[
                int(query_params.get("filter[minPrice]")),
                int(query_params.get("filter[maxPrice]")),
            ],
        ).order_by(sort)

        return queryset


class ReviewCreateView(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Review.objects.filter(product_id=product_id).all()

    def perform_create(self, serializer):
        serializer.save(
            product_id=self.kwargs.get("product_id"), user=self.request.user
        )


class SignInView(APIView):
    def post(self, request):
        data_serialized = list(request.data.keys())[0]
        data = json.loads(data_serialized)
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = user_login(request, data)
            if user is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(APIView):
    def post(self, request):
        data_serialized = list(request.data.keys())[0]
        data = json.loads(data_serialized)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user = user_login(request, data)
            get_or_create_profile_and_avatar(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(RetrieveAPIView, UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        return get_or_create_profile_and_avatar(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AvatarUpdateView(APIView):
    def post(self, request):
        avatar = self.request.user.profile.avatar
        avatar.src = request.FILES["avatar"]
        avatar.save(update_fields=["src"])
        return Response(status=status.HTTP_200_OK)


class PasswordUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = PasswordSerializer(user, data=request.data, partial=True)
        if serializer.is_valid() and check_password(
            serializer.validated_data["currentPassword"], user.password
        ):
            user.password = make_password(serializer.validated_data["newPassword"])
            user.save(update_fields=["password"])
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def user_login(request, data):
    user = authenticate(request, username=data["username"], password=data["password"])
    if user is not None:
        login(request, user)
        print(f"User {data['username']} login")
    else:
        print(f"User with {data} not exist")
    return user


def get_or_create_profile_and_avatar(user):
    try:
        profile = Profile.objects.select_related("user", "avatar").get(user=user)
        print(f"User {user.username} profile exist")
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=user)
        avatar = ProfileAvatar.objects.create(profile=profile)
        print(f"Created avatar {avatar} and profile {profile} for user {user.username}")
    return profile


class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class CategoryListView(ListAPIView):
    queryset = Category.objects.root_nodes()
    serializer_class = CategorySerializer
    pagination_class = None


class SaleListView(ListAPIView):
    queryset = Sale.objects.select_related("product").prefetch_related(
        "product__images"
    )
    serializer_class = SaleSerializer
    pagination_class = CustomPagination


class BasketViewSet(ListAPIView):
    serializer_class = BasketSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        try:
            self.basket = user.basket
        except Basket.DoesNotExist:
            self.basket = Basket.objects.create(user=user)

        queryset = self.basket.basket_items.annotate(
            rating=Avg("product__reviews__rate"),
            reviews_count=Count("product__reviews"),
        ).prefetch_related(
            "product__reviews",
            "product__tags",
            "product__images",
            "product__category",
        )
        return queryset

    def post(self, *args, **kwargs):
        data = self.request.data
        queryset = self.get_queryset()
        basket_item = queryset.filter(product_id=data.get("id"))
        if not basket_item.exists():
            product = Product.objects.get(id=data.get("id"))
            BasketItem.objects.create(basket=self.basket, product=product)
            queryset = self.get_queryset()
        else:
            basket_item.update(count=F("count") + data["count"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, *args, **kwargs):
        data = self.request.data
        queryset = self.get_queryset()
        basket_item = queryset.filter(product_id=data.get("id"))
        basket_item_for_delete = queryset.filter(
            product_id=data.get("id"), count=data["count"]
        )
        if basket_item_for_delete.exists():
            basket_item_for_delete.delete()
        else:
            basket_item.update(count=F("count") - data["count"])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(ListAPIView):
    serializer_class = OrderSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        queryset = user.profile.orders.prefetch_related(
            Prefetch(
                lookup="order_items",
                queryset=OrderItem.objects.annotate(
                    rating=Avg("product__reviews__rate"),
                    reviews_count=Count("product__reviews"),
                ),
            ),
            "order_items__product__reviews",
            "order_items__product__tags",
            "order_items__product__images",
            "order_items__product__category",
        ).annotate(
            total_cost=Sum(F("order_items__product__price") * F("order_items__count"))
        )
        return queryset

    # def post(self, *args, **kwargs):
    #     data = self.request.data
    #     profile = self.request.user.profile
    #     order = Order.objects.create(profile=profile)
    #     for item in data:
    #         product = Product.objects
