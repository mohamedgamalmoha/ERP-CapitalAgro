from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from accounts.fields import PrefixedIDField
from accounts.models import CustomerUser
from orders.enums import OrderStatus


class Order(models.Model):
    id = PrefixedIDField(prefix='ORD', verbose_name=_('Order ID'))
    restaurant = models.ForeignKey('restaurant.Restaurant', on_delete=models.CASCADE, null=True,
                                   related_name='orders', verbose_name=_('Restaurant'))
    customer = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, blank=True, related_name='orders',
                                 verbose_name=_('Customer'))
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING,
                              verbose_name=_('Status'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=_('Total Amount'))
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
        indexes = [
            models.Index(fields=['id'], name='ord_itm_id_index')
        ]

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.product.selling_price
        if self.total_price is None:
            self.total_price = self.quantity * self.unit_price
        self.clean()
        super().save(*args, **kwargs)
