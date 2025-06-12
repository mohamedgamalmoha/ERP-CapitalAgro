import uuid
from typing import Self
from datetime import datetime

from django.db import models


class PrefixedIDField(models.CharField):
    """
    Custom Django field that generates IDs in the format:
    PREFIX-YYYYMMDD-HHMMSS-UUID

    Example: USER-20241215-143022-A1B2C3D4-E5F6-7890-ABCD-EF1234567890
    """

    def __init__(self, prefix: str = "PREFIX", *args, **kwargs) -> None:
        self.prefix = prefix
        # Set max_length to accommodate the full ID format
        # PREFIX (variable) + "-" + YYYYMMDD (8) + "-" + HHMMSS (6) + "-" + UUID (36) = variable + 51
        kwargs.setdefault('max_length', len(prefix) + 51)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)

    def generate_id(self) -> str:
        """
        Generate a new ID in the specified format
        """
        now = datetime.now()
        return f"{self.prefix}-{now.strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4()).upper()}"

    def pre_save(self, model_instance: Self, add: bool) -> str:
        """
        Generate the ID before saving if it's a new instance.
        If the field is already set, it will not change it.

        Args:
            - model_instance: The instance being saved.
            - add: True if this is a new instance, False if updating an existing one.

        Returns:
            - The generated ID or the existing value if it was already set.
        """
        if add and not getattr(model_instance, self.attname):
            value = self.generate_id()
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)
