# Generated by Django 2.2.9 on 2020-02-03 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0022_auto_20200203_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='plate_num',
            field=models.ForeignKey(db_column='plate_num', null=True, on_delete=django.db.models.deletion.SET_NULL, to='Ride_Share.Vehicle'),
        ),
    ]
