import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EducationPlatform.settings")
app = Celery("EducationPlatform")
app.config_from_object("django.conf:settings", namespace='')
app.conf.beat_schedule = {
    'weekly-mail-notification': {
        'task': 'user.tasks.send_weekly_mail_notification',
        'schedule': crontab(hour=18, day_of_week=1),
    }
}
app.autodiscover_tasks()
