# Generated by Django 3.1.3 on 2020-12-02 17:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0012_auto_20201123_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='uuid',
            field=models.UUIDField(editable=False, unique=False, verbose_name='UUID', null=True),
        ),
        migrations.AddField(
            model_name='receipt',
            name='uuid',
            field=models.UUIDField(editable=False, unique=False, verbose_name='UUID', null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='terms',
            field=models.IntegerField(choices=[(100, 'Subscription'), (101, 'Monthly Subscription'), (103, 'Quarterly Subscription'), (106, 'Semi-Annual Subscription'), (112, 'Annual Subscription'), (200, 'Perpetual'), (220, 'One-Time Use')], default=0, verbose_name='Terms'),
        ),
    ]
