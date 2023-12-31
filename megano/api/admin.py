from api.models import (
    Category,
    CategoryImage,
    Product,
    ProductImage,
    ProductTag,
    Profile,
    ProfileAvatar,
    Review,
    Sale,
    Specification,
    Tag,
    Basket,
    BasketItem,
)
from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    classes = ["wide", "collapse"]


class ProductSpecificationInline(admin.StackedInline):
    model = Specification
    classes = ["wide", "collapse"]


class ProductTagInline(admin.StackedInline):
    model = ProductTag
    classes = ["wide", "collapse"]

class BasketItemInline(admin.StackedInline):
    model = BasketItem
    classes = ["wide", "collapse"]


class ProfileAvatarInLine(admin.TabularInline):
    model = ProfileAvatar


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = "pk", "name"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = "pk", "fullName", "user", "phone", "avatar"

    inlines = [ProfileAvatarInLine]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = "pk", "product", "author", "email", "text", "rate", "date"


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = "pk", "product", "salePrice", "dateFrom", "dateTo"


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
        ProductTagInline,
    ]
    list_display = (
        "pk",
        "title",
        "description_short",
        "price",
        "count",
        "archived",
        "category",
    )
    list_display_links = "pk", "title"
    ordering = "-title", "pk"
    search_fields = "title", "description"
    fieldsets = [
        (
            None,
            {
                "fields": (
                    "title",
                    "description",
                    "price",
                    "count",
                    "category",
                    "fullDescription",
                    "freeDelivery",
                    "limited_edition",
                ),
            },
        ),
        (
            "Extra options",
            {
                "fields": ("archived",),
                "classes": ("collapse",),
                "description": "Extra options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


class CategoryImageInLine(admin.StackedInline):
    model = CategoryImage


@admin.register(Category)
class CategoryAdmin(DjangoMpttAdmin):
    inlines = [
        CategoryImageInLine,
    ]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    inlines = [
        BasketItemInline,
    ]
    list_display = "pk", "user"
