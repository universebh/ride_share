# Generated by Django 2.2.9 on 2020-01-31 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0013_auto_20200131_0217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='sharable',
            field=models.BooleanField(blank=True),
        ),
    ]
