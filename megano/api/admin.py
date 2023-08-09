from django.contrib import admin
from django_mptt_admin.admin import DjangoMpttAdmin

from api.models import Product, ProductImage, Category, Tag, Review, Specification, Profile, ProfileAvatar, ProductTag, \
    CategoryImage


class ProductImageInline(admin.StackedInline):
    model = ProductImage
    classes = ["wide", "collapse"]


class ProductSpecificationInline(admin.StackedInline):
    model = Specification
    classes = ["wide", "collapse"]


class ProductTagInline(admin.StackedInline):
    model = ProductTag
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


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
        ProductTagInline,
    ]
    list_display = "pk", "title", "description_short", "price", "count", "archived", "category"
    list_display_links = "pk", "title"
    ordering = "-title", "pk"
    search_fields = "title", "description"
    fieldsets = [
        (None, {
            "fields": (
                "title",
                "description",
                "price",
                "count",
                "category",
                "fullDescription",
                "freeDelivery",
            ),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
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
