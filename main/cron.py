from main.models import Mailing


def send_scheduled_emails():
    """ Вызывает отправку рассылок """
    # выбрать все подходящие рассылки
    mailing_list = Mailing.get_objects_for_send()
    # запустить цикл по этим рассылкам
    for mailing in mailing_list:
        # вызвать метод send
        mailing.send()
