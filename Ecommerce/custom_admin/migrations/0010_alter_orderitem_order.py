# Generated by Django 4.1.5 on 2024-06-25 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('custom_admin', '0009_alter_orderitem_order_alter_orderitem_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='custom_admin.order'),
        ),
    ]