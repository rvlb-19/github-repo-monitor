# Generated by Django 2.2.7 on 2019-11-21 16:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('commits', '0002_auto_20191121_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='commit',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]