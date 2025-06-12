from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save

from workstation.models import WorkstationRawMaterialConsumption


@receiver(post_save, sender=WorkstationRawMaterialConsumption)
def update_raw_material_on_consumption_save(sender, instance, created, **kwargs):
    """
    Update raw material current_quantity when consumption is created or updated
    """
    with transaction.atomic():
        raw_material = instance.raw_material  # Assuming FK field exists

        if created:
            # New consumption record - subtract from current quantity
            raw_material.current_quantity -= instance.quantity_consumed
            raw_material.save(update_fields=['current_quantity'])
        else:
            # Existing record updated - need to handle the difference
            # Get the old quantity from the database
            old_instance = WorkstationRawMaterialConsumption.objects.get(pk=instance.pk)
            old_quantity = getattr(old_instance, '_original_quantity', old_instance.quantity_consumed)

            quantity_difference = instance.quantity_consumed - old_quantity

            if quantity_difference > 0:
                raw_material.current_quantity -= quantity_difference
            elif quantity_difference < 0:
                # Decreased consumption - add back to stock
                raw_material.current_quantity += abs(quantity_difference)

            raw_material.save(update_fields=['current_quantity'])


@receiver(post_delete, sender=WorkstationRawMaterialConsumption)
def update_raw_material_on_consumption_delete(sender, instance, **kwargs):
    """
    Update raw material current_quantity when consumption record is deleted
    """
    with transaction.atomic():
        raw_material = instance.raw_material
        # Add back the consumed quantity to current stock
        raw_material.current_quantity += instance.quantity_consumed
        raw_material.save(update_fields=['current_quantity'])


@receiver(pre_save, sender=WorkstationRawMaterialConsumption)
def store_original_quantity(sender, instance, **kwargs):
    """
    Store original quantity before saving to handle updates properly
    """
    if instance.pk:  # Only for existing instances
        try:
            original = WorkstationRawMaterialConsumption.objects.get(pk=instance.pk)
            instance._original_quantity = original.quantity_consumed
        except WorkstationRawMaterialConsumption.DoesNotExist:
            instance._original_quantity = 0
