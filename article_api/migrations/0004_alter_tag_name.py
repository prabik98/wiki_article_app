# Generated by Django 5.1.3 on 2024-11-21 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article_api', '0003_alter_article_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
