# Generated by Django 4.2.1 on 2023-06-11 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='information',
            field=models.TextField(blank=True, null=True, verbose_name='自定义信息'),
        ),
    ]
