# Generated by Django 4.1.5 on 2024-07-07 06:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin', '0025_admin_panel_authtoken'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Admin_Panel_AuthToken',
        ),
    ]