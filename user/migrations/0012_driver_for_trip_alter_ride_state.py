# Generated by Django 4.1.7 on 2023-05-26 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0011_alter_ride_state_alter_vehicle_vehicle_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='for_trip',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ride',
            name='state',
            field=models.CharField(choices=[('s', 'started'), ('i', 'driver incoming'), ('p', 'pickup ready'), ('o', 'ongoing'), ('f', 'finished'), ('c', 'cancelled')], default='s', max_length=1),
        ),
    ]
