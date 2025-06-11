from django.db import models
from django.contrib.auth.backends import get_user_model

import factory

from accounts.enums import UserRole


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = False
    is_superuser = False
    is_active = True
    role = UserRole.OTHER
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

    @factory.lazy_attribute_sequence
    def username(self, n):
        max_pk = User.objects.aggregate(max_pk=models.Max('pk'))['max_pk'] or 0
        return f'user_{max(max_pk, n) + 1}'

    class Meta:
        model = User
        django_get_or_create = ('username','email')


class InventoryCoordinatorUserFactory(UserFactory):
    role = UserRole.INVENTORY_COORDINATOR

    class Meta:
        model = User
        django_get_or_create = ('username', 'email')


class WorkerUserFactory(UserFactory):
    role = UserRole.WORKER

    class Meta:
        model = User
        django_get_or_create = ('username', 'email')


class TransporterUserFactory(UserFactory):
    role = UserRole.TRANSPORTER

    class Meta:
        model = User
        django_get_or_create = ('username', 'email')
