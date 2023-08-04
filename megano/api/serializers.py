from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import Avg
from rest_framework import serializers

from .models import Product, Review, ProductImage, Specification, Tag, Profile


class ReviewSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", required=False)

    class Meta:
        model = Review
        fields = (
            "author",
            "email",
            "text",
            "rate",
            "date",
        )


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = (
            "src",
            "alt",
        )


class SpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specification
        fields = (
            "name",
            "value",
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
        )


class ProductSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField("calculate_rating")
    reviews = serializers.SerializerMethodField("get_reviews")
    images = serializers.SerializerMethodField("get_images")
    specifications = serializers.SerializerMethodField("get_specifications")
    tags = serializers.SerializerMethodField("get_tags")

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "count",
            "date",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        )
        depth = 1

    def calculate_rating(self, product) -> float:
        rating = product.reviews.aggregate(rating=Avg("rate"))["rating"]
        return rating

    def get_reviews(self, product):
        return ReviewSerializer(product.reviews, many=True).data

    def get_images(self, product):
        return ImageSerializer(product.images, many=True).data

    def get_specifications(self, product):
        return SpecificationSerializer(product.specifications, many=True).data

    def get_tags(self, product):
        return TagSerializer(product.tags, many=True).data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name")
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "name",
            "username",
            "password",
        )

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super(UserSerializer, self).create(validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255, source="user.email")
    class Meta:
        model = Profile
        fields = (
            "fullName",
            "email",
            "phone",
            "avatar",
        )
        depth = 1

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        for k, v in user_data.items():
            setattr(user, k, v)
        user.save()
        profile_data = validated_data
        for k, v in profile_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("password", )
