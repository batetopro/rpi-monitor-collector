# Generated by Django 5.1.5 on 2025-02-13 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_rename_neighbormodel_neighbourmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neighbourmodel',
            name='mask',
            field=models.CharField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='neighbourmodel',
            name='type',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
