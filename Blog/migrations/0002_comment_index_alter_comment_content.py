# Generated by Django 4.2.1 on 2023-06-08 21:20

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='index',
            field=models.IntegerField(default=1, verbose_name='楼层'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='评论内容'),
        ),
    ]
