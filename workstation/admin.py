from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from workstation.models import Workstation, Equipment, WorkstationRawMaterialConsumption, WorkstationPreparedMaterial


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'workstation', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('workstation', )


@admin.register(WorkstationRawMaterialConsumption)
class WorkstationRawMaterialConsumptionAdmin(admin.ModelAdmin):
    list_display = ('workstation', 'raw_material', 'worker', 'quantity_consumed', 'unit', 'transporter',
                    'delivery_date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('workstation', 'raw_material', 'worker', 'transporter', 'unit')
    fieldsets = (
        (
            _("General info"),
            {"fields": ("workstation", "raw_material")},
        ),
        (
            _("Worker info"),
            {"fields": ("worker", "quantity_consumed", "unit")},
        ),
        (
            _("Transporter info"),
            {"fields": ("transporter", "delivery_date")},
        ),
        (
            _("Important dates"),
            {"fields": ( 'created_at', 'updated_at')},
        ),
    )


@admin.register(WorkstationPreparedMaterial)
class WorkstationPreparedMaterialAdmin(admin.ModelAdmin):
    list_display = ('workstation', 'quantity', 'unit', 'preparation_date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('workstation', 'unit')
