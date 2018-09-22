# Generated by Django 2.1.1 on 2018-09-22 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=73)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('gender', models.CharField(max_length=10)),
                ('income', models.IntegerField()),
                ('latitude', models.DecimalField(decimal_places=7, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=7, max_digits=9)),
            ],
        ),
    ]
