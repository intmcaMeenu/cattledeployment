# Generated by Django 5.0.6 on 2024-09-22 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cattle_app', '0018_payment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]