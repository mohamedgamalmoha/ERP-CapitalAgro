from django.db import models
from django.utils.translation import gettext_lazy as _


class Unit(models.TextChoices):
    KG = 'kg', _('Kilogram')
    LITER = 'l', _('Liter')
    PIECE = 'pc', _('Piece')
    METER = 'm', _('Meter')
    GRAM = 'g', _('Gram')
    MILLILITER = 'ml', _('Milliliter')
    BOX = 'box', _('Box')
    PACKET = 'packet', _('Packet')
    BOTTLE = 'bottle', _('Bottle')
    OTHER = 'other', _('Other')


class Status(models.TextChoices):
    ACCEPTED = 'accepted', _('Accepted')
    REJECTED = 'rejected', _('Rejected')


class PackageType(models.TextChoices):
    BOX = 'box', _('Box')
    PACKET = 'packet', _('Packet')
    BOTTLE = 'bottle', _('Bottle')
    OTHER = 'other', _('Other')
