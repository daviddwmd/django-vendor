# Generated by Django 2.2.7 on 2019-11-15 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0020_auto_20191115_0112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'verbose_name_plural': 'purchases'},
        ),
        migrations.AlterField(
            model_name='invoice',
            name='ordered_date',
            field=models.DateField(null=True, verbose_name='Ordered Date'),
        ),
    ]
