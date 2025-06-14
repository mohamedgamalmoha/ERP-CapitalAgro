from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save

from orders.models import OrderItem


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
