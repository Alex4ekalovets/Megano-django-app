from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django_cleanup import cleanup
from imagekit.models import ProcessedImageField
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from pilkit.processors import ResizeToFit


class Category(MPTTModel):
    """Модель категорий товаров"""
    title = models.CharField(max_length=100, null=False, blank=True, verbose_name="Name")
    parent = TreeForeignKey('self', on_delete=models.PROTECT, null=True, blank=True, related_name='subcategories',
                            db_index=True, verbose_name='Parent category')
    slug = models.SlugField()

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title


def category_image_directory_path(instance: "CategoryImage", filename: str) -> str:
    """Создает ссылку на изображения товаров"""
    return "categories/category_{pk}/{filename}".format(
        pk=instance.category.pk,
        filename=filename,
    )


class CategoryImage(models.Model):
    """Модель с изображениями категорий"""
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="image",
        verbose_name="Category"
    )
    src = models.ImageField(upload_to=category_image_directory_path, verbose_name="Link")
    alt = models.CharField(max_length=200, null=False, blank=True, verbose_name="Description")


class Tag(models.Model):
    """Модель тэгов"""
    name = models.CharField(max_length=100, blank=False, null=False, unique=True, verbose_name="Name")

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Модель товара"""
    title = models.CharField(max_length=100, null=False, blank=False, verbose_name="Name")
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, verbose_name="Price")
    count = models.IntegerField(default=0, verbose_name="Count")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation")
    description = models.TextField(null=False, blank=True, verbose_name="Description")
    archived = models.BooleanField(default=False, verbose_name="Archived")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category", verbose_name="Category")
    fullDescription = models.TextField(null=False, blank=True, verbose_name="Full description")
    freeDelivery = models.BooleanField(default=False, verbose_name="Free delivery")
    tags = models.ManyToManyField(Tag, through="ProductTag", related_name="products", verbose_name="Tag")

    def __str__(self):
        return f"{self.title} (pk={self.pk})"

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"


def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    """Создает ссылку на изображения товаров"""
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductTag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Product")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Tag")


@cleanup.select
class ProductImage(models.Model):
    """Модель с изображениями товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Product")
    src = models.ImageField(upload_to=product_images_directory_path, verbose_name="Link")
    alt = models.CharField(max_length=200, null=False, blank=True, verbose_name="Description")


class Review(models.Model):
    """Модель отзыва на товар"""
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="reviews", verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Product")
    author = models.CharField(max_length=191, null=False, blank=False, verbose_name="Author")
    email = models.EmailField(max_length=254, verbose_name="E-mail")
    text = models.TextField(null=False, blank=True, verbose_name="Review text")
    rate = models.SmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ],
        verbose_name="Product rate"
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date of creation")

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"


class Specification(models.Model):
    """Модель характеристик товара"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="Product"
    )
    name = models.CharField(max_length=100, null=False, blank=False, verbose_name="Parameter")
    value = models.CharField(max_length=200, null=False, blank=False, verbose_name="Value")

    class Meta:
        verbose_name = "specification"
        verbose_name_plural = "Specifications"


def avatar_directory_path(instance: "ProfileAvatar", filename: str) -> str:
    """Создает ссылку на аватарку пользователя"""
    return "profiles/profile_{pk}/avatar/{filename}".format(
        pk=instance.profile.pk,
        filename=filename
    )


class Profile(models.Model):
    """Модель профиля пользователя"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{11}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed."
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", verbose_name="User")
    fullName = models.CharField(max_length=150, null=False, blank=True, verbose_name="Full name")
    phone = models.CharField(
        max_length=12,
        validators=[phone_regex],
        unique=True,
        blank=True,
        null=True,
        verbose_name="Phone number"
    )


@cleanup.select
class ProfileAvatar(models.Model):
    """Модель аватарки пользователя"""
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="avatar",
        verbose_name="User profile"
    )
    src = ProcessedImageField(upload_to=avatar_directory_path,
                              processors=[ResizeToFit(291, 291, mat_color=(255, 255, 255))],
                              format='JPEG',
                              options={'quality': 60},
                              default="profiles/default_avatar.png",
                              verbose_name="Link"
                              )
    alt = models.CharField(max_length=128, default="avatar", verbose_name="Description")
