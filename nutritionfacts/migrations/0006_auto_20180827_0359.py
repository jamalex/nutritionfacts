# Generated by Django 2.0 on 2018-08-27 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutritionfacts', '0005_auto_20180112_0047'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('instance_id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('platform', models.CharField(blank=True, max_length=150)),
                ('python_version', models.CharField(blank=True, max_length=100)),
                ('database_id', models.CharField(blank=True, max_length=32)),
                ('node_id', models.CharField(blank=True, max_length=32)),
            ],
        ),
        migrations.RenameField(
            model_name='pingback',
            old_name='instance_id',
            new_name='instance_id_old',
        ),
    ]
