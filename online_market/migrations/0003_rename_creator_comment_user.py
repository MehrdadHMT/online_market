# Generated by Django 4.0.3 on 2022-05-14 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('online_market', '0002_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='user',
            new_name='user',
        ),
    ]