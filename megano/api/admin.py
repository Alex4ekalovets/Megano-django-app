from django.contrib import admin

from api.models import Product, ProductImage, Category, Tag, Review, Specification, Profile, ProfileAvatar


class ProductImageInline(admin.StackedInline):
    model = ProductImage


class ProductSpecificationInline(admin.StackedInline):
    model = Specification


class ProductTagInline(admin.StackedInline):
    model = Tag

class ProfileAvatarInLine(admin.TabularInline):
    model = ProfileAvatar

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = "pk", "fullName", "user", "phone", "avatar"

    inlines = [ProfileAvatarInLine]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = "pk", "title"


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
           "fields": ("title", "description"),
        }),
        ("Price options", {
            "fields": ("price",),
            "classes": ("wide", "collapse"),
        }),
        ("Count options", {
            "fields": ("count",),
            "classes": ("wide", "collapse"),
        }),
        ("Category", {
            "fields": ("category",),
            "classes": ("wide", "collapse"),
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
