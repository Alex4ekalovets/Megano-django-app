from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField

from .models import (
    Category,
    CategoryImage,
    Product,
    ProductImage,
    Profile,
    ProfileAvatar,
    Review,
    Sale,
    Specification,
    Tag,
    Basket,
    BasketItem,
)


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


class ProductImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = (
            "src",
            "alt",
        )

    def get_src(self, instance):
        return instance.src.url


class ProductSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        format="%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)"
    )
    rating = serializers.FloatField()
    reviews = ReviewSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    title = serializers.SerializerMethodField("get_title")
    # В случае, если исправят в соответствии со swagger
    # tags = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field="name"
    # )

    # как указано в контракте в swagger не работает, поэтому оставляем так
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        )

    def get_title(self, instance):
        title = instance.title.replace("/", "-")
        return title


class CatalogSerializer(ProductSerializer):
    rating = serializers.FloatField()
    reviews = serializers.FloatField(source="reviews_count")

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )


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


class ProfileAvatarSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProfileAvatar
        fields = (
            "src",
            "alt",
        )

    def get_src(self, instance):
        return instance.src.url


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, source="user.email")
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "fullName",
            "email",
            "phone",
            "avatar",
        )
        depth = 1

    def get_avatar(self, profile):
        return ProfileAvatarSerializer(profile.avatar).data

    def update(self, profile, validated_data):
        def update_selected_fields(obj, data):
            for k, v in data.items():
                setattr(obj, k, v)
            update_fields = list(data.keys())
            obj.save(update_fields=update_fields)

        user_data = validated_data.pop("user")
        profile_data = validated_data

        update_selected_fields(obj=profile.user, data=user_data)
        update_selected_fields(obj=profile, data=profile_data)
        return profile


class PasswordSerializer(serializers.ModelSerializer):
    currentPassword = serializers.CharField(max_length=128)
    newPassword = serializers.CharField(max_length=128, min_length=5)

    class Meta:
        model = User
        fields = ("currentPassword", "newPassword")


class CategoryImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = CategoryImage
        fields = (
            "src",
            "alt",
        )

    def get_src(self, instance):
        return instance.src.url


class CategorySerializer(serializers.ModelSerializer):
    subcategories = RecursiveField(allow_null=True, many=True)
    image = CategoryImageSerializer()

    class Meta:
        model = Category
        fields = (
            "id",
            "title",
            "image",
            "subcategories",
        )


class SaleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product.id", read_only=True)
    dateFrom = serializers.DateTimeField(format="%m-%d")
    dateTo = serializers.DateTimeField(format="%m-%d")
    price = serializers.DecimalField(
        max_digits=8, decimal_places=2, source="product.price", read_only=True
    )
    title = serializers.CharField(source="product.title", read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = (
            "id",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "title",
            "images",
        )

    def get_images(self, instance):
        images = ProductImageSerializer(instance.product.images, many=True).data
        return images


class BasketSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product.id")
    category = serializers.IntegerField(source="product.category.id")
    price = serializers.DecimalField(
        source="product.price", max_digits=8, decimal_places=2
    )
    date = serializers.DateTimeField(
        source="product.date",
        format="%a %b %d %Y %H:%M:%S %Z%z (Central European Standard Time)",
    )
    title = serializers.CharField(source="product.title")
    description = serializers.CharField(source="product.description")
    freeDelivery = serializers.BooleanField(source="product.freeDelivery")
    images = ProductImageSerializer(many=True, source="product.images")
    tags = TagSerializer(many=True, source="product.tags")
    rating = serializers.FloatField()
    reviews = serializers.FloatField(source="reviews_count")

    class Meta:
        model = BasketItem
        fields = (
            "id",
            "category",
            "price",
            "count",
            "date",
            "title",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        )
