# Generated by Django 5.2.2 on 2025-06-12 20:04

import accounts.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=accounts.fields.PrefixedIDField(editable=False, max_length=54, primary_key=True, serialize=False, unique=True, verbose_name='User ID'),
        ),
    ]
