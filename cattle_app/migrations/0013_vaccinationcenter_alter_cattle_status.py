# Generated by Django 5.0.6 on 2024-09-03 01:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cattle_app', '0012_cattle_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='VaccinationCenter',
            fields=[
                ('center_id', models.AutoField(primary_key=True, serialize=False)),
                ('center_name', models.CharField(max_length=50)),
                ('center_email', models.CharField(max_length=50)),
                ('place', models.TextField(blank=True, max_length=50, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('password', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Vaccination Center',
                'verbose_name_plural': 'Vaccination Centers',
            },
        ),
        migrations.AlterField(
            model_name='cattle',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
