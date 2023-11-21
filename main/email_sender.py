from django.conf import settings
from django.core.mail import send_mail


def send_mail_task(subject, message, recipient_list):
    '''
    Отправляет e-mail пользователю через втроенную функцию send_mail
    :param subject: заголовок сообщения
    :param message: текст сообщения
    :param recipient_list: список e-mail адресов получателей
    '''

    from_email = settings.EMAIL_HOST_USER

    try:
        return send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print(f'Ошибка отправки {e}')
        raise
