from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.IntegerChoices):
    PENDING = 0, _("Pending")
    CONFIRMED = 1, _("Confirmed")
    PREPARING = 2, _("Preparing")
    READY = 3, _('Ready')
    DELIVERED = 4, _('Delivered')
    CANCELLED = 5, _("Cancelled")
