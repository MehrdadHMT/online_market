# Generated by Django 4.0.3 on 2022-05-10 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_market', '0004_alter_shoporder_track_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoporder',
            name='track_id',
            field=models.IntegerField(),
        ),
    ]
