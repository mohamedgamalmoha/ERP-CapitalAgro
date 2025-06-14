from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from restaurant.models import Restaurant, RestaurantPackagedMaterial, ProductCategory, Product, RecipeIngredient


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RestaurantPackagedMaterial)
class RestaurantPackagedMaterialAdmin(admin.ModelAdmin):
    list_display = ('restaurant', 'current_package_quantity', 'unit', 'created_at', 'updated_at')
    list_filter = ('unit',)
    readonly_fields = ('current_package_quantity', 'finished_date', 'created_at', 'updated_at')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("restaurant", "material", "package_material", "initial_package_quantity",
                        "current_package_quantity", "unit", "production_date", "expiration_date")},
        ),
        (
            _("Storage info"),
            {"fields": ("storage_location", "storage_temperature")},
        ),
        (
            _("Transporter info"),
            {"fields": ("transporter", "delivery_date")},
        ),
        (
            _("Important dates"),
            {"fields": ('finished_date', 'created_at', 'updated_at')},
        ),
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class RecipeIngredientInlineAdmin(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'created_at', 'updated_at')
    list_filter = ('is_available', )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [RecipeIngredientInlineAdmin]
