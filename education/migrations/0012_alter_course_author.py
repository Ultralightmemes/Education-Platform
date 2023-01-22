# Generated by Django 4.1.1 on 2023-01-19 17:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('education', '0011_course_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='author',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='created_courses', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
    ]