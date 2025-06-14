from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import post_save, pre_save, post_delete

from orders.enums import OrderStatus
from orders.models import Order, OrderItem


@receiver(pre_save, sender=Order)
def order_status_pre_save(sender, instance, **kwargs):
    """
    Store the previous status before saving to detect status changes
    """
    if instance.pk:
        try:
            instance._previous_status = Order.objects.get(pk=instance.pk).status
        except Order.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    Handle ingredient consumption/restoration based on order status changes
    """
    if created:
        # New order created - no consumption needed yet
        return

    previous_status = getattr(instance, '_previous_status', None)
    current_status = instance.status

    # Define status groups
    consumption_statuses = [OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.DELIVERED]
    non_consumption_statuses = [OrderStatus.PENDING, OrderStatus.CANCELLED]

    # Status change logic
    try:
        with transaction.atomic():
            # Case 1: Moving from non-consumption to consumption status
            if (previous_status in non_consumption_statuses and
                    current_status in consumption_statuses):

                # Validate ingredient availability before consuming
                instance.validate_ingredient_availability()
                instance.consume_order_ingredients()

            # Case 2: Moving from consumption to non-consumption status
            elif (previous_status in consumption_statuses and
                  current_status in non_consumption_statuses):

                instance.restore_order_ingredients()

            # Case 3: Moving between consumption statuses (no action needed)
            elif (previous_status in consumption_statuses and
                  current_status in consumption_statuses):
                ...

            # Case 4: Moving between non-consumption statuses (no action needed)
            elif (previous_status in non_consumption_statuses and
                  current_status in non_consumption_statuses):
                ...

    except ValidationError as e:
        # Re-raise validation errors to prevent status change
        raise ValidationError(f"Cannot change order status: {e}")
    except Exception as e:
        ...


@receiver(pre_save, sender=OrderItem)
def order_item_pre_save(sender, instance, **kwargs):
    """
    Store previous quantity before saving to detect changes
    """
    if instance.pk:
        try:
            previous_item = OrderItem.objects.get(pk=instance.pk)
            instance._previous_quantity = previous_item.quantity
            instance._previous_product_id = previous_item.product_id
        except OrderItem.DoesNotExist:
            instance._previous_quantity = None
            instance._previous_product_id = None
    else:
        instance._previous_quantity = None
        instance._previous_product_id = None


@receiver(post_save, sender=OrderItem)
def handle_order_item_change(sender, instance, created, **kwargs):
    """
    Handle ingredient consumption changes when order items are modified
    """
    from restaurant.models import RestaurantPackagedMaterialConsumption

    order = instance.order

    # Only handle changes for orders in consumption states
    consumption_statuses = [OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.DELIVERED]

    if order.status not in consumption_statuses:
        return

    try:
        with transaction.atomic():
            if created:
                # New order item added to confirmed order - consume ingredients
                instance.consume_ingredients()

            else:
                # Existing order item modified
                previous_quantity = getattr(instance, '_previous_quantity', None)
                previous_product_id = getattr(instance, '_previous_product_id', None)

                # If product or quantity changed, recalculate consumption
                if (previous_quantity != instance.quantity or
                        previous_product_id != instance.product_id):
                    # First, restore ingredients from previous state
                    RestaurantPackagedMaterialConsumption.objects.filter(
                        order_item=instance
                    ).delete()

                    # Then consume for new state
                    instance.consume_ingredients()

    except Exception as e:
       ...


@receiver(post_delete, sender=OrderItem)
def handle_order_item_deletion(sender, instance, **kwargs):
    """
    Restore ingredients when an order item is deleted
    """
    from restaurant.models import RestaurantPackagedMaterialConsumption

    order = instance.order

    # Only handle deletions for orders in consumption states
    consumption_statuses = [OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.DELIVERED]

    if order.status not in consumption_statuses:
        return

    try:
        with transaction.atomic():
            # Get consumption records before they're deleted by cascade
            consumption_records = RestaurantPackagedMaterialConsumption.objects.filter(
                order_item=instance
            ).select_related('restaurant_package_material')

            # Restore ingredients
            for consumption in consumption_records:
                rpm = consumption.restaurant_package_material
                current_qty = rpm.current_package_quantity or 0
                rpm.current_package_quantity = current_qty + consumption.quantity_consumed

                # Unmark finished date if applicable
                if rpm.finished_date and rpm.current_package_quantity > 0:
                    rpm.finished_date = None

                rpm.save()

    except Exception as e:
        ...
