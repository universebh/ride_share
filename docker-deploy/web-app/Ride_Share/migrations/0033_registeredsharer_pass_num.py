# Generated by Django 2.2.9 on 2020-02-05 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ride_Share', '0032_auto_20200205_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredsharer',
            name='pass_num',
            field=models.IntegerField(null=True),
        ),
    ]
