# Generated by Django 5.2.2 on 2025-06-10 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_rename_packaging_type_packagedmaterial_package_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='packagedmaterial',
            old_name='stored_location',
            new_name='storage_location',
        ),
        migrations.RenameField(
            model_name='packagedmaterial',
            old_name='stored_temperature',
            new_name='storage_temperature',
        ),
        migrations.RenameField(
            model_name='readymaterial',
            old_name='stored_location',
            new_name='storage_location',
        ),
        migrations.RenameField(
            model_name='readymaterial',
            old_name='stored_temperature',
            new_name='storage_temperature',
        ),
    ]
