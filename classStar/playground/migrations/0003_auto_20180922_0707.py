# Generated by Django 2.0.5 on 2018-09-22 07:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0002_auto_20180922_0706'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='user',
            new_name='created_by',
        ),
    ]
