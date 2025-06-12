from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from inventory.models import PackagedMaterial  
from inventory.enums import Unit
from accounts.enums import UserRole 

class Distribution(models.Model):
    packaged_material = models.ForeignKey(
        PackagedMaterial,
        on_delete=models.CASCADE,
        related_name='distributions',
        null=True
    )
    market = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='market_distributions',
        limit_choices_to={'role': UserRole.MARKET}
    )
    transporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transporter_distributions',
        limit_choices_to={'role': UserRole.TRANSPORTER}
    )
    quantity_distributed = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, choices=Unit.choices)
    distribution_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.packaged_material} ➝ {self.market} ({self.quantity_distributed} {self.unit})"
