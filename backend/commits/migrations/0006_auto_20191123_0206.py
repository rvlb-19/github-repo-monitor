# Generated by Django 2.2.7 on 2019-11-23 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commits', '0005_remove_commit_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commit',
            name='created_at',
        ),
        migrations.AddField(
            model_name='commit',
            name='url',
            field=models.CharField(default='', max_length=255),
        ),
    ]