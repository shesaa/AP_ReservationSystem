# Generated by Django 4.2.8 on 2024-01-28 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal_app', '0004_alter_appointment_appointment_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]