from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.IntegerChoices):
    ADMIN = 0, _("Admin")
    INVENTORY_COORDINATOR = 1, _("Inventory Coordinator")
    WORKER = 2, _("Worker")
    TRANSPORTER = 3, _("Transporter")
    CUSTOMER = 4, _("Customer")
    OTHER = 5, _("Other")
