from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from inventory.models import Supplier, Category, RawMaterial, ReadyMaterial, PackagedMaterial


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
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
    list_display = ('material_name', 'category', 'supplier', 'current_quantity', 'unit', 'created_at', 'updated_at')
    list_filter = ('unit', 'status')
    readonly_fields = ('current_quantity', 'created_at', 'updated_at')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("supplier", "category", "material_name", "initial_quantity", "current_quantity", "unit",
                        "received_date", "production_date", "expiration_date")},
        ),
        (
            _("Coordinator info"),
            {"fields": ("inventory_coordinator", "quality_score", "status", "note")},
        ),
        (
            _("Storage info"),
            {"fields": ("storage_location", "storage_temperature")},
        ),
        (
            _("Important dates"),
            {"fields": ( 'created_at', 'updated_at')},
        ),
    )


@admin.register(ReadyMaterial)
class ReadyMaterialAdmin(admin.ModelAdmin):
    list_display = ('workstation_prepared_material', 'initial_quantity', 'unit', 'created_at', 'updated_at')
    list_filter = ('unit',)
    readonly_fields = ('current_quantity', 'created_at', 'updated_at')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("workstation_prepared_material", "initial_quantity", "current_quantity", "unit")},
        ),
        (
            _("Coordinator info"),
            {"fields": ("inventory_coordinator", "quality_score", "note")},
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
            {"fields": ('created_at', 'updated_at')},
        ),
    )


@admin.register(PackagedMaterial)
class PackagedMaterialAdmin(admin.ModelAdmin):
    list_display = ('ready_material', 'created_at', 'updated_at')
    list_filter = ('unit',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("quantity", "unit", "package_date", "package_type")},
        ),
        (
            _("Worker info"),
            {"fields": ("worker", "note")},
        ),
        (
            _("Storage info"),
            {"fields": ("storage_location", "storage_temperature")},
        ),
        (
            _("Important dates"),
            {"fields": ('created_at', 'updated_at')},
        ),
    )
