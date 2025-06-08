from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from inventory.models import Distributor, Category, RawMaterial


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(RawMaterial)
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('distributor', 'category', 'name', 'quantity', 'unit', 'created_at', 'updated_at')
    list_filter = ('unit', 'status', 'inventory_coordinator')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("distributor", "category", "name", "quantity", "unit", "expiration_date")}
        ),
        (
            _("Coordinator info"),
            {"fields": ("inventory_coordinator", "quality_check", "status", "stored_location", "note")},
        ),
        (
            _("Important dates"),
            {"fields": ('created_at', 'updated_at')}
        ),
    )
