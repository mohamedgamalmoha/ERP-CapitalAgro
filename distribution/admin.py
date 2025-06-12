from django.contrib import admin
from distribution.models import Distribution
from accounts.models import TransporterUser, User
from workstation.models import Workstation, WorkstationPreparedMaterial


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = (
        'packaged_material',
        'market',
        'transporter',
        'quantity_distributed',
        'unit',
        'distribution_date',
        'created_at',
    )
    autocomplete_fields = ('packaged_material', 'market', 'transporter')
    search_fields = (
        'packaged_material__ready_material__workstation_raw_material__raw_material__material_name',
        'market__username',
        'transporter__username',
    )
    list_filter = ('distribution_date', 'market', 'transporter')
    ordering = ('-distribution_date',)
