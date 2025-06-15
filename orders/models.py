from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator

from accounts.fields import PrefixedIDField
from accounts.models import CustomerUser
from orders.enums import (OrderStatus, ORDER_STATUS_SEQUENCE, ORDER_STATUS_APPLY_CONSUMPTION,
                          ORDER_STATUS_AVAILABILITY_CHECK, ORDER_STATUS_APPLY_RESTORATION,
                          ORDER_STATUS_DENY_ITEMS_MODIFICATION)


class Order(models.Model):
    id = PrefixedIDField(prefix='ORD', verbose_name=_('Order ID'))
    restaurant = models.ForeignKey('restaurant.Restaurant', on_delete=models.CASCADE, null=True,
                                   related_name='orders', verbose_name=_('Restaurant'))
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, blank=True, related_name='orders',
                                 verbose_name=_('Customer'))
    status = models.PositiveIntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING,
                              verbose_name=_('Status'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       verbose_name=_('Total Amount'))
    order_date = models.DateTimeField(default=timezone.now, blank=True, null=True, verbose_name=_('Order Date'))
    delivered_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Delivered Date'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        indexes = [
            models.Index(fields=['id'], name='ord_id_index')
        ]

    def clean(self):
        # Check if this is an existing instance to validate status transitions
        try:
            old_instance = Order.objects.get(pk=self.pk)
            old_status = old_instance.status
        except Order.DoesNotExist:  # New instance, no validation needed
            return

         # Check if status transition is valid
        if not self.is_valid_status_transition(old_status, self.status):
            old_status_display = OrderStatus(old_status).label
            new_status_display = OrderStatus(self.status).label
            raise ValidationError({
                'status': _(
                    f"Invalid status transition from '{old_status_display}' to '{new_status_display}'."
                )
            })

        # Validate that the order has a restaurant and customer
        if self.is_valid_status_availability_check(self.status):
            self.validate_ingredient_availability()

        # Check if ingredients should be consumed based on status change
        if self.is_valid_status_consumption(old_status, self.status):
            self.validate_ingredient_availability()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def validate_ingredient_availability(self):
        """
        Validate that all ingredients required for the order are available in sufficient quantities.
        """
        errors = []

        for order_item in self.order_items.all():
            ingredient_errors = order_item.validate_ingredient_availability()
            if ingredient_errors:
                errors.extend([
                    f"Product '{order_item.product.name}' (Qty: {order_item.quantity}): {error}"
                    for error in ingredient_errors
                ])

        if errors:
            raise ValidationError({
                'ingredients': _('Insufficient ingredients available: ') + '; '.join(errors)
            })

    @transaction.atomic
    def consume_order_ingredients(self):
        """
        Consume ingredients for all items in an order
        """
        for order_item in self.order_items.all():
            order_item.consume_ingredients()

    @transaction.atomic
    def restore_order_ingredients(self):
        """
        Restore ingredients by reversing consumption records for an order
        """
        from restaurant.models import RestaurantPackagedMaterialConsumption

        # Get all consumption records for this order
        consumption_records = RestaurantPackagedMaterialConsumption.objects.filter(
            order_item__order=self
        ).select_related('restaurant_package_material')

        # Group by restaurant package material to batch updates
        material_updates = {}

        for consumption in consumption_records:
            rpm = consumption.restaurant_package_material
            if rpm.id not in material_updates:
                material_updates[rpm.id] = {
                    'material': rpm,
                    'total_to_restore': 0,
                    'consumption_ids': []
                }

            material_updates[rpm.id]['total_to_restore'] += consumption.quantity_consumed
            material_updates[rpm.id]['consumption_ids'].append(consumption.id)

        # Update material quantities and delete consumption records
        for update_data in material_updates.values():
            rpm = update_data['material']
            restore_qty = update_data['total_to_restore']

            # Restore the quantity
            current_qty = rpm.current_package_quantity or 0
            rpm.current_package_quantity = current_qty + restore_qty

            # If material was marked as finished, unmark it
            if rpm.finished_date and rpm.current_package_quantity > 0:
                rpm.finished_date = None

            rpm.save()

        # Delete all consumption records for this order
        RestaurantPackagedMaterialConsumption.objects.filter(
            id__in=[
                consumption_id
                for update_data in material_updates.values()
                for consumption_id in update_data['consumption_ids']
            ]
        ).delete()

    @staticmethod
    def is_valid_status_transition(from_status: ORDER_STATUS_SEQUENCE, to_status: OrderStatus) -> bool:
        """
        Check if a status transition is valid according to ORDER_STATUS_SEQUENCE.
        """
        # Allow keeping the same status
        if from_status == to_status:
            return True

        # Check if the transition is allowed
        allowed_transitions = ORDER_STATUS_SEQUENCE.get(from_status, [])
        return to_status in allowed_transitions

    @staticmethod
    def is_valid_status_availability_check(status: OrderStatus) -> bool:
        """
        Check if the status is valid for availability checks.
        """
        return status in ORDER_STATUS_AVAILABILITY_CHECK

    @staticmethod
    def is_valid_status_consumption(from_status: ORDER_STATUS_SEQUENCE, to_status: OrderStatus) -> bool:
        return to_status in ORDER_STATUS_APPLY_CONSUMPTION.get(from_status, [])

    @staticmethod
    def is_valid_status_restoration(from_status: ORDER_STATUS_SEQUENCE, to_status: OrderStatus) -> bool:
        """
        Check if a status restoration is valid according to ORDER_STATUS_APPLY_RESTORATION.
        """
        return to_status in ORDER_STATUS_APPLY_RESTORATION.get(from_status, [])


class OrderItem(models.Model):
    id = PrefixedIDField(prefix='ORD-ITM', verbose_name=_('Order Item ID'))
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name=_('Order'))
    product = models.ForeignKey('restaurant.Product', on_delete=models.CASCADE, related_name='order_items',
                                verbose_name=_('product'))
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name=_('Quantity'))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                     verbose_name=_('Unit Price'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                      verbose_name=_('Total Price'))
    note = models.TextField(null=True, blank=True, verbose_name=_('Note'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        unique_together = ('order', 'product')
        indexes = [
            models.Index(fields=['id'], name='ord_itm_id_index')
        ]

    def clean(self):
        # Deny creation or updated when order os ready or prepared
        # if self.order and not self.is_valid_items_modification(self.order.status):
        #     raise ValidationError(
        #         _('Cannot modify order items when order is ready or preparing.')
        #     )

        # Validate ingredient availability for new order items or quantity changes
        if self.order and self.order.restaurant:
            ingredient_errors = self.validate_ingredient_availability()
            if ingredient_errors:
                raise ValidationError({
                    'quantity': _('Insufficient ingredients available: ') + '; '.join(ingredient_errors)
                })

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.product.selling_price
        if self.total_price is None:
            self.total_price = self.quantity * self.unit_price
        self.clean()
        super().save(*args, **kwargs)

    def get_required_ingredients(self):
        """
        Calculate the total quantity of each ingredient required for this order item.
        Returns a dictionary with material_id as key and required quantity as value.
        """
        from restaurant.models import RecipeIngredient

        required_ingredients = {}

        # Get all recipe ingredients for this product
        recipe_ingredients = RecipeIngredient.objects.filter(product=self.product)

        for ingredient in recipe_ingredients:
            material_id = ingredient.material_id
            required_quantity = ingredient.quantity_consumed * self.quantity

            if material_id in required_ingredients:
                required_ingredients[material_id] += required_quantity
            else:
                required_ingredients[material_id] = required_quantity

        return required_ingredients

    def get_available_material_quantity(self, material_id):
        """
        Get the total available quantity for a specific material in the restaurant.
        This includes all non-expired materials minus any reserved quantities.
        """
        from restaurant.models import RestaurantPackagedMaterial

        # Get all restaurant packaged materials for this material that are not expired
        restaurant_materials = RestaurantPackagedMaterial.objects.filter(
            restaurant__id=self.order.restaurant.id,
            material__id=material_id,
            current_package_quantity__gt=0
        )

        # Calculate total available quantity
        total_available = sum(
            rpm.current_package_quantity
            for rpm in restaurant_materials
        )

        return total_available

    def validate_ingredient_availability(self):
        """
        Validate that all ingredients for this order item are available in sufficient quantities.
        Returns a list of error messages if validation fails.
        """
        from inventory.models import Material

        errors = []
        required_ingredients = self.get_required_ingredients()

        if not required_ingredients:
            return errors  # No ingredients required

        for material_id, required_quantity in required_ingredients.items():
            available_quantity = self.get_available_material_quantity(material_id)

            if available_quantity < required_quantity:
                try:
                    material = Material.objects.get(id=material_id)
                    material_name = material.material_name
                except Material.DoesNotExist:
                    material_name = f"Material ID {material_id}"

                errors.append(
                    f"{material_name}: Required {required_quantity}, Available {available_quantity}"
                )

        return errors

    @transaction.atomic
    def consume_ingredients(self):
        """
        Consume the ingredients required for this order item.
        This should be called when the order is being prepared.
        """
        from restaurant.models import RestaurantPackagedMaterial, RestaurantPackagedMaterialConsumption

        required_ingredients = self.get_required_ingredients()

        for material_id, required_quantity in required_ingredients.items():
            remaining_to_consume = required_quantity

            # Get available materials sorted by expiration date (FIFO)
            available_materials = RestaurantPackagedMaterial.objects.filter(
                restaurant__id=self.order.restaurant.id,
                material__id=material_id,
                current_package_quantity__gt=0
            ).order_by('expiration_date', 'created_at')

            for material in available_materials:
                if remaining_to_consume <= 0:
                    break

                consumed_quantity = remaining_to_consume
                try:
                    material.reduce_current_package_quantity(quantity=consumed_quantity)
                except ValidationError:
                    consumed_quantity = material.current_package_quantity
                    material.reduce_current_package_quantity(quantity=consumed_quantity)
                finally:
                    remaining_to_consume -= consumed_quantity
                    RestaurantPackagedMaterialConsumption.objects.create(
                        order_item=self,
                        restaurant_package_material=material,
                        material=material.material,
                        quantity_consumed=consumed_quantity,
                    )

    @staticmethod
    def is_valid_items_modification(order_status: OrderStatus) -> bool:
        """
        Check if items can be modified based on the order status.
        """
        return order_status not in ORDER_STATUS_DENY_ITEMS_MODIFICATION
