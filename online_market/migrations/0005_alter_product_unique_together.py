# Generated by Django 4.0.3 on 2022-05-18 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online_market', '0004_alter_product_product_quantity'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('type', 'brand', 'name')},
        ),
    ]
