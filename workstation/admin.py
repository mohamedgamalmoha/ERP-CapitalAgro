from django.contrib import admin

from workstation.models import Workstation, WorkstationRawMaterial, WorkstationPreparedMaterial


@admin.register(Workstation)
class WorkstationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WorkstationRawMaterial)
class WorkstationRawMaterialAdmin(admin.ModelAdmin):
    list_display = ('workstation', 'raw_material', 'worker', 'delivery_date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('workstation', )


@admin.register(WorkstationPreparedMaterial)
class WorkstationPreparedMaterialAdmin(admin.ModelAdmin):
    list_display = ('workstation', 'raw_material', 'quantity', 'unit', 'preparation_date', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('workstation', 'unit')
