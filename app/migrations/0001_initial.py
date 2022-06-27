# Generated by Django 4.0.4 on 2022-05-30 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('department', models.CharField(choices=[('hr', 'Human Resources'), ('finance', 'Finance'), ('engineering', 'Engineering'), ('marketing', 'Marketing'), ('sales', 'Sales')], max_length=20)),
                ('salary', models.PositiveIntegerField()),
            ],
        ),
    ]