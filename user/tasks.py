from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from user.models import User


@shared_task
def send_weekly_mail_notification():
    subject = 'Продолжи работу над курсами!'
    for user in User.objects.all():
        courses = user.courses.order_by("update_date")
        if courses:
            message = f'Продолжи работу над курсом {user.courses.order_by("update_date")[0].name}'
        else:
            message = 'Начни работу над новым курсом!'
        send_mail(subject, message, settings.EMAIL_HOST_USER, (user.email, ))
    return "Sending weekly mail is done"
