# Generated by Django 5.2 on 2025-04-14 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.RemoveField(
            model_name='pricemodifier',
            name='product',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='PriceModifier',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
