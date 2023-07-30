import json

from django.contrib.auth import authenticate, login
from rest_framework import status, pagination
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from shopapp.models import Product, Review
from shopapp.serializers import ProductSerializer, ReviewSerializer, LoginSerializer, UserSerializer


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


class ReviewCreateView(CreateAPIView):
    serializer_class = ReviewSerializer
    # permission_classes = [IsAuthenticated]

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





