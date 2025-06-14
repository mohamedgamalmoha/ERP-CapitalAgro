from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.IntegerChoices):
    PENDING = 0, _("Pending")
    CONFIRMED = 1, _("Confirmed")
    PREPARING = 2, _("Preparing")
    READY = 3, _('Ready')
    DELIVERED = 4, _('Delivered')
    CANCELLED = 5, _("Cancelled")


ORDER_STATUS_SEQUENCE = {
    OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
    OrderStatus.CONFIRMED: [OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.CANCELLED],
    OrderStatus.PREPARING: [OrderStatus.READY],
    OrderStatus.READY: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELLED: [],
}

ORDER_STATUS_AVAILABILITY_CHECK = [
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PREPARING
]

ORDER_STATUS_APPLY_CONSUMPTION = {
    OrderStatus.CONFIRMED: [
        OrderStatus.PREPARING,
        OrderStatus.READY
    ]
}

ORDER_STATUS_APPLY_RESTORATION = {
    OrderStatus.PENDING: [
        OrderStatus.CANCELLED
    ],
    OrderStatus.CONFIRMED: [
        OrderStatus.CANCELLED
    ],
}

ORDER_STATUS_DENY_ITEMS_MODIFICATION = [
    OrderStatus.PREPARING,
    OrderStatus.READY,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELLED
]
