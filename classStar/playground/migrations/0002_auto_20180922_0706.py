# Generated by Django 2.0.5 on 2018-09-22 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('playground', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='creator',
            new_name='user',
        ),
    ]
