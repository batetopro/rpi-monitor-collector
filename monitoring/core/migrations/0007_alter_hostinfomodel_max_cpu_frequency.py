# Generated by Django 5.1.5 on 2025-02-03 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_devicemodel_cpu_frequency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostinfomodel',
            name='max_cpu_frequency',
            field=models.FloatField(null=True),
        ),
    ]
