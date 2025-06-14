from django.db import models
from django.core.validators import ValidationError, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.fields import PrefixedIDField
from accounts.models import TransporterUser
from inventory.enums import Unit


class Restaurant(models.Model):
    id = PrefixedIDField(prefix='RS', verbose_name=_('Restaurant ID'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    location = models.CharField(max_length=255, verbose_name=_('Location'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Restaurant')
        verbose_name_plural = _('Restaurant')
        indexes = [
            models.Index(fields=['id'], name='rs_id_index')
        ]

    def __str__(self):
        return self.name


class RestaurantPackagedMaterial(models.Model):
    id = PrefixedIDField(prefix='RPM', verbose_name=_('Restaurant Package Material ID'))

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, null=True,
                                   related_name='restaurant_package_materials', verbose_name=_('Restaurant'))
    material = models.ForeignKey('inventory.Material', on_delete=models.CASCADE, verbose_name=_('Material'))
    package_material = models.OneToOneField('inventory.PackagedMaterial', on_delete=models.CASCADE, null=True,
                                            verbose_name=_('Package Material'))
    initial_package_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Initial Package Quantity')
    )
    current_package_quantity = models.PositiveIntegerField(null=True, blank=True,
                                                           verbose_name=_('Current Package Quantity'))
    unit = models.CharField(max_length=20, choices=Unit.choices, null=True, blank=True, verbose_name=_('Unit'))

    transporter = models.ForeignKey(TransporterUser, on_delete=models.CASCADE,
                                    related_name='restaurant_delivered_ready_materials', verbose_name=_('Transporter'))
    delivery_date = models.DateField(default=timezone.now, null=True, blank=True, verbose_name=_('Delivery Date'))

    production_date = models.DateField(null=True, blank=True, verbose_name=_('Production Date'))
    expiration_date = models.DateField(null=True, blank=True, verbose_name=_('Expiration Date'))

    storage_location = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('Stored Location'))
    storage_temperature = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Stored Temperature'))

    finished_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Delivery Date'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Restaurant Packaged Material')
        verbose_name_plural = _('Restaurant Packaged Materials')
        indexes = [
            models.Index(fields=['id'], name='rpm_id_index')
        ]

    def clean(self):
        # Validate expiration date is after production date
        if self.production_date and self.expiration_date:
            if self.expiration_date <= self.production_date:
                raise ValidationError(
                    {'expiration_date': 'Expiration date must be after production date.'}
                )

    def save(self, *args, **kwargs):
        # Change finished date when it is totally consumed
        if not self.pk and self.current_package_quantity is None:
            self.current_package_quantity = self.initial_package_quantity
        self.clean()
        super().save(*args, **kwargs)

    def reduce_current_package_quantity(self, quantity: int) -> None:
        if quantity > self.current_package_quantity:
            raise ValidationError(
                {'current_package_quantity': _('Not enough quantity')}
            )
        self.current_package_quantity -= quantity
        if self.current_package_quantity == 0:
            self.finished_date = timezone.now()
        self.save()


class RestaurantPackagedMaterialConsumption(models.Model):
    id = PrefixedIDField(prefix='CONS', verbose_name=_('Consumption ID'))

    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.CASCADE,
                                   related_name='material_consumptions', verbose_name=_('Order Item'))
    restaurant_package_material = models.ForeignKey(RestaurantPackagedMaterial, on_delete=models.CASCADE,
                                                     verbose_name=_('Restaurant Package Material'))
    material = models.ForeignKey('inventory.Material', on_delete=models.CASCADE, verbose_name=_('Material'))

    quantity_consumed = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantity Consumed')
    )
    consumption_date = models.DateTimeField(default=timezone.now, null=True, blank=True,
                                            verbose_name=_('Consumption Date'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Material Consumption')
        verbose_name_plural = _('Material Consumptions')
        indexes = [
            models.Index(fields=['id'], name='cons_id_index')
        ]


class ProductCategory(models.Model):
    id = PrefixedIDField(prefix='P-CAT', verbose_name=_('Product ID'))
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Name'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        indexes = [
            models.Index(fields=['id'], name='pcat_id_index')
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    id = PrefixedIDField(prefix='PROD', verbose_name=_('Product ID'))
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, verbose_name=_('Category'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Selling Price'))
    is_available = models.BooleanField(default=True, verbose_name=_('Is Available'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        indexes = [
            models.Index(fields=['id'], name='prod_id_index')
        ]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    id = PrefixedIDField(prefix='ING', verbose_name=_('Product ID'))
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name=_('Product')
    )
    material = models.ForeignKey('inventory.Material', on_delete=models.CASCADE, verbose_name=_('Material'))
    quantity_consumed = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name=_('Quality Consumed')
    )
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Recipe Ingredient')
        verbose_name_plural = _('Recipe Ingredients')
        indexes = [
            models.Index(fields=['id'], name='ing_id_index')
        ]
