# Generated by Django 4.1.3 on 2022-11-24 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appsae', '0017_merge_20221124_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='telephone',
            field=models.CharField(max_length=10),
        ),
    ]
