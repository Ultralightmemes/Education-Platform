# Generated by Django 4.1.1 on 2022-09-23 15:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ('position',), 'verbose_name': 'Урок', 'verbose_name_plural': 'Уроки'},
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ('position',), 'verbose_name': 'Тема', 'verbose_name_plural': 'Темы'},
        ),
        migrations.AddField(
            model_name='theme',
            name='position',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Позиция'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='theme',
            unique_together={('position', 'course')},
        ),
    ]