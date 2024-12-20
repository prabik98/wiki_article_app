# Generated by Django 5.1.3 on 2024-11-20 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='tags',
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(to='article_api.tag'),
        ),
    ]
