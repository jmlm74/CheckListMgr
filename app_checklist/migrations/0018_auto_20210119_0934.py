# Generated by Django 3.1.2 on 2021-01-19 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_checklist', '0017_auto_20210119_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checklistdone',
            name='cld_reminder',
            field=models.BooleanField(default=None, null=True),
        ),
    ]