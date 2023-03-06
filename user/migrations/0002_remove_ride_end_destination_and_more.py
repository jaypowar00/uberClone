# Generated by Django 4.1.7 on 2023-03-04 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ride',
            name='end_destination',
        ),
        migrations.RemoveField(
            model_name='ride',
            name='start_destination',
        ),
        migrations.AddField(
            model_name='ride',
            name='end_destination_lat',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='ride',
            name='end_destination_lon',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='ride',
            name='start_destination_lat',
            field=models.FloatField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='ride',
            name='start_destination_lon',
            field=models.FloatField(default=None, null=True),
        ),
    ]