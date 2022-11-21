from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_subscribe_mail(email, name, course_name):
    subject = 'Подписка на курс'
    message = f'Привет, {name}, спасибо за подписку на курс {course_name}'
    send_mail(subject, message, settings.EMAIL_HOST_USER, (email, ))
    return 'sent'
