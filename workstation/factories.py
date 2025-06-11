import factory

from inventory.enums import Unit
from workstation.models import Workstation, Equipment, WorkstationRawMaterialConsumption, WorkstationPreparedMaterial


class WorkstationFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('company')
    description = factory.Faker('text', max_nb_chars=200)
    location = factory.Faker('address')
    max_daily_capacity = factory.Faker('random_int', min=1, max=1000)
    categories_handled = factory.RelatedFactoryList(
        'inventory.factories.CategoryFactory',
        # factory_related_name='workstations',
        size=3
    )

    class Meta:
        model = Workstation
        django_get_or_create = ('name',)


class EquipmentFactory(factory.django.DjangoModelFactory):
    workstation = factory.SubFactory(WorkstationFactory)
    name = factory.Faker('food_workstation_equipment', category=factory.SelfAttribute('..workstation.name'))
    last_maintenance_date = factory.Faker('date_time_this_year', before_now=True)
    calibration_date = factory.Faker('date_time_this_year', before_now=True)

    class Meta:
        model = Equipment
        django_get_or_create = ('name',)


class WorkstationRawMaterialConsumptionFactory(factory.django.DjangoModelFactory):
    workstation = factory.SubFactory(WorkstationFactory)
    raw_material = factory.SubFactory('inventory.factories.RawMaterialFactory')
    worker = factory.SubFactory('accounts.factories.WorkerUserFactory')
    quantity_consumed = factory.Faker('random_int', min=1, max=100)
    unit = factory.Faker('random_element', elements=Unit.choices)
    transporter = factory.SubFactory('accounts.factories.TransporterUserFactory')
    delivery_date = factory.Faker('date_time_this_year')

    class Meta:
        model = WorkstationRawMaterialConsumption
        django_get_or_create = ('workstation', 'raw_material', 'worker')


class WorkstationPreparedMaterialFactory(factory.django.DjangoModelFactory):
    workstation = factory.SubFactory(WorkstationFactory)
    raw_material = factory.SubFactory('inventory.factories.RawMaterialFactory')
    quantity = factory.Faker('random_int', min=1, max=100)
    unit = factory.Faker('random_element', elements=Unit.choices)
    preparation_date = factory.Faker('date_time_this_year', before_now=True)

    class Meta:
        model = WorkstationPreparedMaterial
        django_get_or_create = ('workstation', 'raw_material')
