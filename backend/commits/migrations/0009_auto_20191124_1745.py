# Generated by Django 2.2.7 on 2019-11-24 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commits', '0008_commit_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commit',
            old_name='created_at',
            new_name='date',
        ),
    ]
