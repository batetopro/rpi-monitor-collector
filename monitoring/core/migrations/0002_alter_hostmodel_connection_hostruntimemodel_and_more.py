# Generated by Django 5.1.5 on 2025-02-18 13:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostmodel',
            name='connection',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='host', to='core.sshconnectionmodel'),
        ),
        migrations.CreateModel(
            name='HostRuntimeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu_frequency', models.PositiveBigIntegerField(null=True)),
                ('cpu_temperature', models.PositiveBigIntegerField(null=True)),
                ('cpu_usage', models.PositiveBigIntegerField()),
                ('used_ram', models.PositiveBigIntegerField()),
                ('disk_io_read_bytes', models.PositiveBigIntegerField(null=True)),
                ('disk_io_write_bytes', models.PositiveBigIntegerField(null=True)),
                ('net_io_bytes_recv', models.PositiveBigIntegerField(null=True)),
                ('net_io_bytes_sent', models.PositiveBigIntegerField(null=True)),
                ('time_saved', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.hostmodel')),
            ],
            options={
                'verbose_name': 'Host Runtime',
                'verbose_name_plural': 'Host Runtimes',
            },
        ),
        migrations.DeleteModel(
            name='HostUsageModel',
        ),
    ]
