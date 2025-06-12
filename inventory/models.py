from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator

from accounts.fields import PrefixedIDField
from accounts.models import InventoryCoordinatorUser, TransporterUser, WorkerUser
from inventory.enums import Unit, Status, PackageType


class Supplier(models.Model):
    id = PrefixedIDField(prefix='SUPPLIER', verbose_name=_('Supplier ID'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Supplier Name'))
    contact_info = models.TextField(null=True, blank=True, verbose_name=_('Contact Information'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        indexes = [
            models.Index(fields=['id'], name='supplier_id_index')
        ]

    def __str__(self):
        return self.name


class Category(models.Model):
    id = PrefixedIDField(prefix='CAT', verbose_name=_('Category ID'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    requires_temperature_control = models.BooleanField(default=False, verbose_name=_('Requires Temperature Control'))
    max_processing_time_hours = models.PositiveIntegerField(
        null=True, blank=True, verbose_name=_('Max Processing Time (Hours)')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        indexes = [
            models.Index(fields=['id'], name='category_id_index')
        ]

    def __str__(self):
        return self.name


class RawMaterial(models.Model):
    id = PrefixedIDField(prefix='RM', verbose_name=_('Raw Material ID'))

    # Supplier and category
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='raw_materials', verbose_name=_('Supplier')
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='raw_materials', verbose_name=_('Category')
    )

    # Material details
    material_name = models.CharField(max_length=100, null=True, verbose_name=_('Material Name'))
    initial_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Initial Quantity'))
    current_quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Current Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))

    # Dates
    production_date = models.DateField(null=True, blank=True, verbose_name=_('Production Date'))
    expiration_date = models.DateField(null=True, blank=True, verbose_name=_('Expiration Date'))

    # Quality and status
    inventory_coordinator = models.ForeignKey(
        InventoryCoordinatorUser,
        on_delete=models.CASCADE,
        related_name='raw_materials',
        verbose_name=_('Inventory Coordinator')
    )
    quality_score = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_('Quality Score'),
        help_text=_('Quality score from 0 to 10')
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACCEPTED, verbose_name=_('Status'))
    received_date = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name=_('Received Date'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    # Storage details
    storage_location = models.CharField(max_length=100, null=True, verbose_name=_('Storage Location'))
    storage_temperature = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Storage Temperature'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Raw Material')
        verbose_name_plural = _('Raw Materials')
        indexes = [
            models.Index(fields=['id'], name='raw_mat_id_index')
        ]

    def clean(self):
        # Validate expiration date is after production date
        if self.production_date and self.expiration_date:
            if self.expiration_date <= self.production_date:
                raise ValidationError(
                    {'expiration_date': 'Expiration date must be after production date.'}
                )

        # Validate current_quantity <= initial_quantity
        if self.current_quantity > self.initial_quantity:
            raise ValidationError(
                {'current_quantity': 'Current quantity cannot exceed initial quantity.'}
            )

    def save(self, *args, **kwargs):
        # Set current quantity to initial on first save
        if not self.pk and not self.current_quantity:
            self.current_quantity = self.initial_quantity
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.material_name

    def reduce_quantity(self, quantity):
        if quantity > self.current_quantity:
            raise ValueError(
                "Not enough quantity available to reduce."
            )
        self.current_quantity -= quantity
        self.save()

    def increase_quantity(self, quantity):
        if quantity < 0:
            raise ValueError(
                "Cannot increase quantity by a negative amount."
            )
        self.current_quantity += quantity
        self.save()


class ReadyMaterial(models.Model):
    id = PrefixedIDField(prefix='RM-READY', verbose_name=_('Ready Material ID'))

    workstation_prepared_material = models.OneToOneField('workstation.WorkstationPreparedMaterial',
                                                 on_delete=models.CASCADE, null=True, related_name='ready_materials',
                                                 verbose_name=_('Raw Material'))

    inventory_coordinator = models.ForeignKey(InventoryCoordinatorUser, on_delete=models.CASCADE,
                                              related_name='ready_materials', verbose_name=_('Inventory Coordinator'))
    quality_score = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)],
                                                verbose_name=_('Quality Score'))

    initial_quantity = models.PositiveIntegerField(default=0, verbose_name=_('Initial Quantity'))
    current_quantity = models.PositiveIntegerField(null=True,blank=True, verbose_name=_('Current Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    storage_location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stored Location'))
    storage_temperature = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Stored Temperature'))

    transporter = models.ForeignKey(TransporterUser, on_delete=models.CASCADE, related_name='delivered_ready_materials',
                                verbose_name=_('Transporter'))
    delivery_date = models.DateField(default=timezone.now, null=True, blank=True, verbose_name=_('Delivery Date'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Ready Material')
        verbose_name_plural = _('Ready Materials')
        indexes = [
            models.Index(fields=['id'], name='raw_mat_ready_id_index')
        ]

    def clean(self):
        # Ensure consumed quantity doesn't exceed available raw material quantity
        if self.workstation_prepared_material:
            if self.initial_quantity > self.workstation_prepared_material.quantity:
                raise ValidationError(
                    {'initial_quantity': f'Only {self.workstation_prepared_material.quantity} units available.'}
                )
            if self.unit != self.workstation_prepared_material.unit:
                raise ValidationError(
                    {'unit': f'Only {self.workstation_prepared_material.unit} unit is acceptable.'}
                )

    def save(self, *args, **kwargs):
        # Set current quantity to initial on first save
        if not self.pk and not self.current_quantity:
            self.current_quantity = self.initial_quantity
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id


class PackagedMaterial(models.Model):
    id = PrefixedIDField(prefix='PM', verbose_name=_('Packaged Material ID'))
    ready_material = models.ForeignKey(ReadyMaterial, on_delete=models.CASCADE, related_name='packed_materials',
                                       verbose_name=_('Ready Material'))

    worker = models.ForeignKey(WorkerUser, on_delete=models.CASCADE, related_name='packed_materials',
                                          verbose_name=_('Worker'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE, verbose_name=_('Unit'))
    package_date = models.DateField(null=True, blank=True, verbose_name=_('Package Date'))
    package_type = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.BOX,
                                      verbose_name=_('Packaging Type'))
    package_quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], null=True,
                                                   verbose_name=_('Package Quantity'))
    package_unit = models.CharField(max_length=20, choices=Unit.choices, default=Unit.PIECE,
                                    verbose_name=_('Package Unit'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))

    production_date = models.DateField(null=True, blank=True, verbose_name=_('Production Date'))
    expiration_date = models.DateField(null=True, blank=True, verbose_name=_('Expiration Date'))

    storage_location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stored Location'))
    storage_temperature = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Stored Temperature'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Packaged Material')
        verbose_name_plural = _('Packaged Materials')
        indexes = [
            models.Index(fields=['id'], name='pac_mat_id_index')
        ]

    def clean(self):
        # Ensure packaged quantity doesn't exceed ready material quantity
        if self.quantity > self.ready_material.current_quantity:
            raise ValidationError(
                {'quantity': f'Only {self.ready_material.current_quantity} units available.'}
            )

        # Validate expiration date is after production date
        if self.production_date and self.expiration_date:
            if self.expiration_date <= self.production_date:
                raise ValidationError(
                    {'expiration_date': 'Expiration date must be after production date.'}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id
