from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import WorkerUser, TransporterUser
from inventory.enums import Unit
from inventory.models import RawMaterial, Category


class Workstation(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    max_daily_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Max Daily Capacity'))
    categories_handled = models.ManyToManyField(Category, blank=True, verbose_name=_('Categories Handled'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Workstation')
        verbose_name_plural = _('Workstations')

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Equipment Name'))
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE, related_name='equipment')
    last_maintenance_date = models.DateField(null=True, blank=True)
    calibration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Equipment')
        verbose_name_plural = _('Equipment')

    def __str__(self):
        return f"{self.name}"


class WorkstationRawMaterialConsumption(models.Model):
    workstation = models.ForeignKey(
        Workstation, on_delete=models.CASCADE, related_name='raw_materials', verbose_name=_('Workstation')
    )
    raw_material = models.ForeignKey(
        RawMaterial, on_delete=models.CASCADE, related_name='workstations', verbose_name=_('Raw Material')
    )

    worker = models.ForeignKey(
        WorkerUser, on_delete=models.CASCADE, related_name='workstation_raw_materials', verbose_name=_('Worker')
    )
    quantity_consumed = models.PositiveIntegerField(verbose_name=_('Quantity Consumed'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))

    transporter = models.ForeignKey(
        TransporterUser,
        on_delete=models.CASCADE,
        related_name='workstation_delivered_raw_materials',
        verbose_name=_('Transporter')
    )
    delivery_date = models.DateField(null=True, blank=True, verbose_name=_('Delivery Date'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Raw Material Consumption')
        verbose_name_plural = _('Raw Materials Consumption')

    def __str__(self):
        return f"{self.workstation.name} - {self.raw_material.name}"
    # TODO: Signal for updating raw material quantity in inventory when consumed


class WorkstationPreparedMaterial(models.Model):
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE, related_name='prepared_products',
                                    verbose_name=_('Workstation'))
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='prepared_products',
                                     verbose_name=_('Raw Material'))
    quantity = models.PositiveIntegerField(verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    preparation_date = models.DateField(null=True, blank=True, verbose_name=_('Preparation Date'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Workstation Prepared Material')
        verbose_name_plural = _('Workstation Prepared Materials')
        unique_together = ('workstation', 'raw_material')

    def __str__(self):
        return f"{self.workstation.name} - {self.raw_material.name} ({self.quantity})"
