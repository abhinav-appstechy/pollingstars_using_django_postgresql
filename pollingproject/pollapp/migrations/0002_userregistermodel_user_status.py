# Generated by Django 5.0.6 on 2024-05-08 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pollapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userregistermodel',
            name='user_status',
            field=models.BooleanField(default=False),
        ),
    ]