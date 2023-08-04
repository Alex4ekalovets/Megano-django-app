import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, pagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Product, Review, Profile, ProfileAvatar
from api.serializers import ProductSerializer, ReviewSerializer, LoginSerializer, UserSerializer, ProfileSerializer, \
    PasswordSerializer


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            "items": data,
            "currentPage": self.page.paginator.count,
            "nextPage": self.get_next_link(),
            "previousPage": self.get_previous_link(),
            "lastPage": self.get_next_link(),
        })


class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CatalogListView(ListAPIView):
    queryset = Product.objects.all().order_by("pk")
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
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


class LoginView(APIView):

    def post(self, request):
        data_unicode = request.body.decode("utf-8")
        data = json.loads(data_unicode)
        serializer = LoginSerializer(data=data)
        if serializer.is_valid():
            user = authenticate(
                request,
                username=data["username"],
                password=data["password"]
            )
            if user is not None:
                login(request, user)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserCreateView(APIView):

    def post(self, request):
        data_unicode = request.body.decode("utf-8")
        data = json.loads(data_unicode)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileViewSet(RetrieveAPIView, UpdateModelMixin):
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    def post(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AvatarUpdateView(View):
    def post(self, request):
        user = self.request.user
        avatar, _ = ProfileAvatar.objects.get_or_create(profile=user.profile)
        avatar.src = request.FILES["avatar"]
        avatar.save()
        return HttpResponse(status="200")


class PasswordUpdateView(UpdateAPIView):
    serializer_class = PasswordSerializer

    def get_object(self):
        return self.request.user

    def post(self, request):
        instance = self.get_object()
        data = request.data
        old_password = data.pop("currentPassword")
        data["password"] = make_password(data.pop("newPassword"))
        serializer = self.get_serializer(instance, data=data, partial=False)
        if check_password(old_password, instance.password) and serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
