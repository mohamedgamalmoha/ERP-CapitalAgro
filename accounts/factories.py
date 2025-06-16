from django.contrib.auth.backends import get_user_model

import factory

from accounts.enums import UserRole
from accounts.models import InventoryCoordinatorUser, WorkerUser, TransporterUser


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_staff = False
    is_superuser = False
    is_active = True
    role = UserRole.OTHER
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')

    class Meta:
        model = User
        django_get_or_create = ('username','email')


class InventoryCoordinatorUserFactory(UserFactory):
    role = UserRole.INVENTORY_COORDINATOR

    class Meta:
        model = InventoryCoordinatorUser
        django_get_or_create = ('username', 'email')


class WorkerUserFactory(UserFactory):
    role = UserRole.WORKER

    class Meta:
        model = WorkerUser
        django_get_or_create = ('username', 'email')


class TransporterUserFactory(UserFactory):
    role = UserRole.TRANSPORTER

    class Meta:
        model = TransporterUser
        django_get_or_create = ('username', 'email')
