# Generated by Django 4.1.7 on 2023-03-01 14:55

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('public_id', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('name', models.CharField(max_length=150)),
                ('username', models.CharField(default='', max_length=80, unique=True)),
                ('phone', models.CharField(blank=True, default=None, max_length=20, null=True, unique=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female')], max_length=1)),
                ('account_type', models.CharField(choices=[('R', 'Regular'), ('D', 'Driver')], default='R', max_length=1)),
                ('about', models.TextField(blank=True, default=None, null=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_staff', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=256)),
                ('amount', models.FloatField()),
                ('date', models.DateField()),
                ('status', models.CharField(choices=[('s', 'success'), ('f', 'failed')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='TripLocations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=128)),
                ('thumbnail', models.URLField()),
                ('description', models.CharField(max_length=128)),
                ('location', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_number', models.CharField(max_length=50)),
                ('seat_capacity', models.IntegerField()),
                ('mileage', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Regular',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_destination', models.CharField(max_length=128)),
                ('price', models.FloatField()),
                ('state', models.CharField(choices=[('s', 'started'), ('i', 'driver incoming'), ('p', 'pickup ready'), ('o', 'ongoing'), ('f', 'finished')], default='s', max_length=1)),
                ('otp_verified', models.BooleanField(default=False)),
                ('driver', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='driver_user', to=settings.AUTH_USER_MODEL)),
                ('end_destination', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='user.triplocations')),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='user.payment')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_user', to=settings.AUTH_USER_MODEL)),
                ('user_history', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='ride_history', to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to='user.vehicle')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('comment', models.CharField(blank=True, max_length=500, null=True)),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='from_user', to=settings.AUTH_USER_MODEL)),
                ('to_driver', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='to_driver', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('driver_license', models.CharField(blank=True, max_length=50, null=True)),
                ('vehicle', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.vehicle')),
            ],
        ),
    ]
