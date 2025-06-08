from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from accounts.models import InventoryCoordinatorUser, TransporterUser, WorkerUser
from inventory.enums import Unit, Status


class Distributor(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Distributor Name'))
    contact_info = models.TextField(null=True, blank=True, verbose_name=_('Contact Information'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.name


class RawMaterial(models.Model):
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name='raw_materials',
                                    verbose_name=_('Distributor'))

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='raw_materials',
                                 verbose_name=_('Category'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Raw Material Name'))
    quantity = models.PositiveIntegerField(default=0,
                                           verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    expiration_date = models.DateField(null=True, blank=True, verbose_name=_('Expiration Date'))

    inventory_coordinator = models.ForeignKey(InventoryCoordinatorUser, on_delete=models.CASCADE,
                                              related_name='raw_materials', verbose_name=_('Inventory Coordinator'))
    quality_check = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)],
                                                verbose_name=_('Quality Check'))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACCEPTED, verbose_name=_('Status'))
    stored_location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stored Location'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.name


class ReadyMaterial(models.Model):
    workstation_raw_material = models.ForeignKey('workstation.WorkstationPreparedMaterial',
                                                 on_delete=models.CASCADE, related_name='ready_materials',
                                                 verbose_name=_('Raw Material'))

    inventory_coordinator = models.ForeignKey(InventoryCoordinatorUser, on_delete=models.CASCADE,
                                              related_name='raw_materials', verbose_name=_('Inventory Coordinator'))
    quality_check = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)],
                                                verbose_name=_('Quality Check'))
    stored_location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stored Location'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    transporter = models.ForeignKey(TransporterUser, on_delete=models.CASCADE, related_name='ready_materials',
                                verbose_name=_('Transporter'))
    delivery_date = models.DateField(null=True, blank=True, verbose_name=_('Delivery Date'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return f"{self.workstation_raw_material.name} - {self.quantity} {self.unit}"


class PackagedMaterial(models.Model):
    ready_material = models.ForeignKey(ReadyMaterial, on_delete=models.CASCADE, related_name='packed_materials',
                                       verbose_name=_('Ready Material'))

    worker = models.ForeignKey(WorkerUser, on_delete=models.CASCADE, related_name='packed_materials',
                                          verbose_name=_('Worker'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    package_date = models.DateField(null=True, blank=True, verbose_name=_('Package Date'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    def __str__(self):
        return self.ready_material
