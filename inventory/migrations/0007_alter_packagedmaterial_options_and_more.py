# Generated by Django 5.2.2 on 2025-06-12 19:59

import accounts.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('inventory', '0006_alter_rawmaterial_received_date'),
        ('workstation', '0002_workstation_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='packagedmaterial',
            options={'verbose_name': 'Packaged Material', 'verbose_name_plural': 'Packaged Materials'},
        ),
        migrations.AlterModelOptions(
            name='readymaterial',
            options={'verbose_name': 'Ready Material', 'verbose_name_plural': 'Ready Materials'},
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=54, primary_key=True, serialize=False, unique=True, verbose_name='Category ID'),
        ),
        migrations.AlterField(
            model_name='packagedmaterial',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=53, primary_key=True, serialize=False, unique=True, verbose_name='Packaged Material ID'),
        ),
        migrations.AlterField(
            model_name='rawmaterial',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=53, primary_key=True, serialize=False, unique=True, verbose_name='Raw Material ID'),
        ),
        migrations.AlterField(
            model_name='readymaterial',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=59, primary_key=True, serialize=False, unique=True, verbose_name='Ready Material ID'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=59, primary_key=True, serialize=False, unique=True, verbose_name='Supplier ID'),
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['id'], name='category_id_index'),
        ),
        migrations.AddIndex(
            model_name='packagedmaterial',
            index=models.Index(fields=['id'], name='pac_mat_id_index'),
        ),
        migrations.AddIndex(
            model_name='rawmaterial',
            index=models.Index(fields=['id'], name='raw_mat_id_index'),
        ),
        migrations.AddIndex(
            model_name='readymaterial',
            index=models.Index(fields=['id'], name='raw_mat_ready_id_index'),
        ),
        migrations.AddIndex(
            model_name='supplier',
            index=models.Index(fields=['id'], name='supplier_id_index'),
        ),
    ]
