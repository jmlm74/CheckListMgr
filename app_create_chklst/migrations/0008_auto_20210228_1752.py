# Generated by Django 3.1.7 on 2021-02-28 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_create_chklst', '0007_auto_20210228_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cat_heading',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cat_heading', to='app_create_chklst.heading'),
        ),
        migrations.AddField(
            model_name='line',
            name='line_heading',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='line_heading', to='app_create_chklst.heading'),
        ),
    ]
