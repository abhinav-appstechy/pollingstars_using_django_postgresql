# Generated by Django 5.0.6 on 2024-05-09 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pollapp', '0009_poll_choices'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Choices',
        ),
        migrations.DeleteModel(
            name='Poll',
        ),
    ]