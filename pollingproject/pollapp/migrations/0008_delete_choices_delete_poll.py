# Generated by Django 5.0.6 on 2024-05-09 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pollapp', '0007_poll_due_date_poll_image'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Choices',
        ),
        migrations.DeleteModel(
            name='Poll',
        ),
    ]
