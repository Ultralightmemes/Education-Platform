import os
from datetime import timedelta

import dotenv
from celery import Celery
from celery.schedules import crontab
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '.env')
dotenv.read_dotenv(env_file)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EducationPlatform.settings")
app = Celery("EducationPlatform")

# Comment while using docker

app.config_from_object("django.conf:settings", namespace='')

app.conf.beat_schedule = {
    'weekly-mail-notification': {
        'task': 'user.tasks.send_weekly_mail_notification',
        'schedule': timedelta(seconds=30),
        # 'schedule': crontab(hour=18, day_of_week=1),
    }
}
app.autodiscover_tasks()
