# Generated by Django 5.1.5 on 2025-02-19 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_networkinterfacemodel_addresses_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hostmodel',
            name='net_io_counters',
            field=models.JSONField(null=True),
        ),
    ]
