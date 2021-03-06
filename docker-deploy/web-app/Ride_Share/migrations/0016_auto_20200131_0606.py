# Generated by Django 2.2.9 on 2020-01-31 06:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0015_auto_20200131_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharer',
            name='rideid',
            field=models.ForeignKey(db_column='rideid', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Ride_Share.Ride'),
        ),
        migrations.AlterField(
            model_name='sharer',
            name='sharerid',
            field=models.ForeignKey(db_column='sharerid', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
