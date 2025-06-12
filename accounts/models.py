from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from accounts.enums import UserRole
from accounts.fields import PrefixedIDField
from accounts.managers import (CustomUserManager, InventoryCoordinatorUserManager, WorkerUserManager,
                               TransporterUserManager)


class User(AbstractUser):
    id = PrefixedIDField(prefix='USR', verbose_name=_('User ID'))

    base_role = UserRole.OTHER

    role = models.PositiveSmallIntegerField(choices=UserRole.choices, verbose_name=_('Role'))

    REQUIRED_FIELDS = ['email', 'role']

    objects = CustomUserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ('date_joined', )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class InventoryCoordinatorUser(User):
    base_role = UserRole.INVENTORY_COORDINATOR

    objects = InventoryCoordinatorUserManager()

    class Meta:
        proxy = True


class WorkerUser(User):
    base_role = UserRole.WORKER

    objects = WorkerUserManager()

    class Meta:
        proxy = True


class TransporterUser(User):
    base_role = UserRole.TRANSPORTER

    objects = TransporterUserManager()

    class Meta:
        proxy = True
