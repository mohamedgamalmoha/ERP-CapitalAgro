from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import pre_save, post_save

from orders.models import Order, OrderItem


@receiver(pre_save, sender=Order)
def store_old_order_status(sender, instance, **kwargs):
    """
    Store the old status before saving.
    """
    if instance.pk:
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def handle_ingredient_consumption(sender, instance, created, **kwargs):
    """
    Handle ingredient consumption/restoration after successful save.
    """
    if not created and hasattr(instance, '_old_status') and instance._old_status is not None:
        old_status = instance._old_status

        # Check if ingredients should be consumed based on status change
        if instance.is_valid_status_consumption(old_status, instance.status):
            instance.consume_order_ingredients()

        # Check if ingredients should be restored based on status change
        if instance.is_valid_status_restoration(old_status, instance.status):
            instance.restore_order_ingredients()

    # Clean up the temporary attribute
    if hasattr(instance, '_old_status'):
        delattr(instance, '_old_status')


@receiver(post_save, sender=OrderItem)
def update_order_total_amount(sender, instance, **kwargs):
    """
    Update the total amount of the order when an OrderItem is saved.
    """
    with transaction.atomic():
        order = instance.order
        order_items = order.order_items.all()
        order.total_amount = sum(item.total_price for item in order_items)
        order.save()
