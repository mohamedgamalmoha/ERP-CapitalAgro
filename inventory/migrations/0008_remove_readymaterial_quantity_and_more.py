# Generated by Django 5.2.2 on 2025-06-12 21:38

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_packagedmaterial_options_and_more'),
        ('workstation', '0004_alter_workstationpreparedmaterial_unique_together_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readymaterial',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='readymaterial',
            name='workstation_raw_material',
        ),
        migrations.AddField(
            model_name='readymaterial',
            name='current_quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Current Quantity'),
        ),
        migrations.AddField(
            model_name='readymaterial',
            name='initial_quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Initial Quantity'),
        ),
        migrations.AddField(
            model_name='readymaterial',
            name='workstation_prepared_material',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ready_materials', to='workstation.workstationpreparedmaterial', verbose_name='Raw Material'),
        ),
        migrations.AlterField(
            model_name='readymaterial',
            name='delivery_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Delivery Date'),
        ),
    ]
