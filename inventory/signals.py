from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save

from inventory.models import PackagedMaterial


@receiver(post_save, sender=PackagedMaterial)
def update_ready_material_on_packaging_save(sender, instance, created, **kwargs):
    """
    Update ready material current_quantity when packaging is created or updated
    """
    with transaction.atomic():
        ready_material = instance.ready_material

        if created:
            # New packaging record - subtract from current quantity
            ready_material.current_quantity -= instance.quantity
            ready_material.save(update_fields=['current_quantity'])
        else:
            # Existing record updated - need to handle the difference
            # Get the old quantity from the stored original value
            old_quantity = getattr(instance, '_original_quantity', instance.quantity)

            quantity_difference = instance.quantity - old_quantity

            if quantity_difference > 0:
                # Increased packaging quantity
                ready_material.current_quantity -= quantity_difference
            elif quantity_difference < 0:
                # Decreased packaging quantity - add back to stock
                ready_material.current_quantity += abs(quantity_difference)

            ready_material.save(update_fields=['current_quantity'])


@receiver(post_delete, sender=PackagedMaterial)
def update_ready_material_on_packaging_delete(sender, instance, **kwargs):
    """
    Update ready material current_quantity when packaging record is deleted
    """
    with transaction.atomic():
        ready_material = instance.ready_material
        # Add back the packaged quantity to current stock
        ready_material.current_quantity += instance.quantity
        ready_material.save(update_fields=['current_quantity'])


@receiver(pre_save, sender=PackagedMaterial)
def store_original_packaging_quantity(sender, instance, **kwargs):
    """
    Store original quantity before saving to handle updates properly
    """
    if instance.pk:  # Only for existing instances
        try:
            original = PackagedMaterial.objects.get(pk=instance.pk)
            instance._original_quantity = original.quantity
        except PackagedMaterial.DoesNotExist:
            instance._original_quantity = 0
