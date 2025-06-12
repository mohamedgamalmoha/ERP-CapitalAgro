from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.fields import PrefixedIDField
from accounts.models import WorkerUser, TransporterUser
from inventory.enums import Unit
from inventory.models import RawMaterial, Category


class Workstation(models.Model):
    id = PrefixedIDField(prefix='WS', verbose_name=_('Workstation ID'))
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
        indexes = [
            models.Index(fields=['id'], name='ws_id_index')
        ]

    def __str__(self):
        return self.name


class Equipment(models.Model):
    id = PrefixedIDField(prefix='WS-EQ', verbose_name=_('Equipment ID'))
    name = models.CharField(max_length=100, verbose_name=_('Equipment Name'))
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE, related_name='equipment')
    last_maintenance_date = models.DateField(null=True, blank=True)
    calibration_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Equipment')
        verbose_name_plural = _('Equipment')
        indexes = [
            models.Index(fields=['id'], name='eq_id_index')
        ]

    def __str__(self):
        return self.name


class WorkstationRawMaterialConsumption(models.Model):
    id = PrefixedIDField(prefix='WS-RM', verbose_name=_('Consumption ID'))

    workstation = models.ForeignKey(
        Workstation, on_delete=models.CASCADE, related_name='raw_materials', verbose_name=_('Workstation')
    )
    raw_material = models.ForeignKey(
        RawMaterial, on_delete=models.CASCADE, related_name='workstations', verbose_name=_('Raw Material')
    )

    worker = models.ForeignKey(
        WorkerUser, on_delete=models.CASCADE, related_name='workstation_raw_materials', verbose_name=_('Worker')
    )
    quantity_consumed = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name=_('Quantity Consumed')
    )
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))

    transporter = models.ForeignKey(
        TransporterUser,
        on_delete=models.CASCADE,
        related_name='workstation_delivered_raw_materials',
        verbose_name=_('Transporter')
    )
    delivery_date = models.DateTimeField(default=timezone.now, null=True, blank=True, verbose_name=_('Delivery Date'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Raw Material Consumption')
        verbose_name_plural = _('Raw Materials Consumption')
        indexes = [
            models.Index(fields=['id'], name='ws_rm_id_index')
        ]

    def clean(self):
        # Ensure consumed quantity doesn't exceed available raw material quantity
        if self.raw_material:
            if self.quantity_consumed > self.raw_material.current_quantity:
                raise ValidationError(
                    {'quantity_consumed': f'Only {self.raw_material.current_quantity} units available.'}
                )
            if self.unit != self.raw_material.unit:
                raise ValidationError(
                    {'unit': f'Only {self.raw_material.units} unit is acceptable.'}
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id


class WorkstationPreparedMaterial(models.Model):
    id = PrefixedIDField(prefix='WS-PM', verbose_name=_('Prepared Material ID'))
    workstation_raw_material_consumption = models.OneToOneField(WorkstationRawMaterialConsumption,
                                                                 on_delete=models.CASCADE, null=True,
                                                                verbose_name=_('Workstation Raw Material Consumption'))
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    preparation_date = models.DateTimeField(default=timezone.now, null=True, blank=True,
                                            verbose_name=_('Preparation Date'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Workstation Prepared Material')
        verbose_name_plural = _('Workstation Prepared Materials')
        indexes = [
            models.Index(fields=['id'], name='ws_prepared_mat_id_index')
        ]

    def clean(self):
        # Ensure consumed quantity doesn't exceed available raw material quantity
        if self.workstation_raw_material_consumption:
            if self.quantity > self.workstation_raw_material_consumption.quantity_consumed:
                raise ValidationError(
                    {
                        'quantity':
                            f'Only {self.workstation_raw_material_consumption.quantity_consumed} units available.'
                    }
                )
            if self.unit != self.workstation_raw_material_consumption.unit:
                raise ValidationError(
                    {'unit': f'Only {self.workstation_raw_material_consumption.units} unit is acceptable.'}
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id
