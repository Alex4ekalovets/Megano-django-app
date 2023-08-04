from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django_cleanup import cleanup
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFit


class Category(models.Model):
    """Модель категорий товаров"""
    title = models.CharField(max_length=100, null=False, blank=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.title} (pk={self.pk})"


class Product(models.Model):
    """Модель товара"""
    title = models.CharField(max_length=100, null=False, blank=False)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=False, blank=True)
    archived = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    fullDescription = models.TextField(null=False, blank=True)
    freeDelivery = models.BooleanField(default=False)

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


class ProductImage(models.Model):
    """Модель с изображениями товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    src = models.ImageField(upload_to=product_images_directory_path)
    alt = models.CharField(max_length=200, null=False, blank=True)


class Tag(models.Model):
    """Модель тэгов"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100, blank=False, null=False, db_index=True)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"


class Review(models.Model):
    """Модель отзыва на товар"""
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.CharField(max_length=191, null=False, blank=False)
    email = models.EmailField(max_length=254)
    text = models.TextField(null=False, blank=True)
    rate = models.SmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"


class Specification(models.Model):
    """Модель характеристик товара"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    name = models.CharField(max_length=100, null=False, blank=False)
    value = models.CharField(max_length=200, null=False, blank=False)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    fullName = models.CharField(max_length=150, null=False, blank=True)
    phone = models.CharField(max_length=12, validators=[phone_regex], unique=True, blank=True, null=True)


@cleanup.select
class ProfileAvatar(models.Model):
    """Модель аватарки пользователя"""
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="avatar")
    src = ProcessedImageField(upload_to=avatar_directory_path,
                              processors=[ResizeToFit(291, 291, mat_color=(255, 255, 255))],
                              format='JPEG',
                              options={'quality': 60},
                              default="profiles/default_avatar.png",
                              verbose_name="Link"
                              )
    alt = models.CharField(max_length=128, default="avatar", verbose_name="Description")





