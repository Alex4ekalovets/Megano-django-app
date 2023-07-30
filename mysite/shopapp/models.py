from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100, null=False, blank=True)

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.title} (pk={self.pk})"


class Product(models.Model):
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
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    src = models.ImageField(upload_to=product_images_directory_path)
    alt = models.CharField(max_length=200, null=False, blank=True)


class Tag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100, blank=False, null=False, db_index=True)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="user")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.CharField(max_length=191, null=False, blank=False)
    email = models.EmailField(max_length=254)
    text = models.TextField(null=False, blank=True)
    rate = models.SmallIntegerField(
        default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ])
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "review"
        verbose_name_plural = "reviews"


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="specifications")
    name = models.CharField(max_length=100, null=False, blank=False)
    value = models.CharField(max_length=200, null=False, blank=False)

    class Meta:
        verbose_name = "specification"
        verbose_name_plural = "Specifications"
