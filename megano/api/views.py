import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, pagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Product, Review, Profile, ProfileAvatar, Tag, Category
from api.serializers import ProductSerializer, ReviewSerializer, LoginSerializer, UserSerializer, ProfileSerializer, \
    PasswordSerializer, TagSerializer, CategorySerializer


class CatalogPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            "items": data,
            "currentPage": self.page.paginator.count,
            "nextPage": self.get_next_link(),
            "previousPage": self.get_previous_link(),
            "lastPage": self.get_next_link(),
        })


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related("tags")
    serializer_class = ProductSerializer


class CatalogListView(ListAPIView):
    queryset = Product.objects.all().order_by("pk")
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = [
        "title",
        "description",
        "price",
    ]
    ordering_fields = [
        "title",
        "price",
    ]


class ReviewCreateView(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return Review.objects.filter(product_id=product_id).all()

    def perform_create(self, serializer):
        serializer.save(
            product_id=self.kwargs.get("product_id"),
            user=self.request.user
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
        if serializer.is_valid() and check_password(serializer.validated_data["currentPassword"], user.password):
            user.password = make_password(serializer.validated_data["newPassword"])
            user.save(update_fields=["password"])
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def user_login(request, data):
    user = authenticate(
        request,
        username=data["username"],
        password=data["password"]
    )
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
