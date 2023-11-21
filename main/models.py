import datetime
from django.db import models
from django.utils import timezone

from main.email_sender import send_mail_task

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    email = models.EmailField(verbose_name='почта')
    full_name = models.CharField(max_length=150, verbose_name='ФИО')
    comments = models.TextField(**NULLABLE, verbose_name='комментарий')

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Message(models.Model):
    subject = models.CharField(max_length=150, verbose_name='тема письма')
    body = models.TextField(verbose_name='тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    TIME_CHOICES = (
        ('daily', 'Раз в день'),
        ('weekly', 'Раз в неделю'),
        ('monthly', 'Раз в месяц')
    )

    STATUS_CHOICES = (
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена')
    )

    start_time = models.DateTimeField(verbose_name='старт рассылки', default=timezone.now())
    completion_time = models.DateTimeField(verbose_name='завершение рассылки', default=timezone.now())
    frequency = models.CharField(max_length=15, choices=TIME_CHOICES, verbose_name='периодичность')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='Статус', default='created')
    name = models.CharField(max_length=255, verbose_name='наименование', default='новая рассылка')
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, **NULLABLE, verbose_name='сообщение')
    emails = models.ManyToManyField(Client, verbose_name='Клиенты')
    last_sent = models.DateTimeField(**NULLABLE, verbose_name='последняя отправка')

    def get_status(self):
        """ Метод для получения статуса рассылки """

        return self.status

    @classmethod
    def get_objects_for_send(cls):
        """ Возвращает список рассылок для отправки """

        now = timezone.now()
        objects_list = []

        for m in cls.objects.all():
            # Условие, если нет даты последней отправки,
            # или с даты последней отправки прошло больше одного дня, больше 7 дней, больше 30 дней
            is_daily_valid = not m.last_sent or m.last_sent <= now - datetime.timedelta(days=1)
            is_weekly_valid = not m.last_sent or m.last_sent <= now - datetime.timedelta(days=7)
            is_monthly_valid = not m.last_sent or m.last_sent <= now - datetime.timedelta(days=30)

            if all([
                # время и дата окончания больше или равно текущему времени
                m.frequency == 'daily',
                # last_sended должен быть вчерашним днем
                is_daily_valid,
                # статус должен быть либо created либо completed
                m.status in ['created', 'completed'],
                # время начала меньше или равно текущему времени
                m.start_time.time() < now.time(),
                # время и дата  начала меньше или равно текущему времени
                m.start_time < now,
                # время и дата окончания больше или равно текущему времени
                now < m.completion_time
            ]):
                objects_list.append(m)

            elif all([
                # время и дата окончания больше или равно текущему времени
                m.frequency == 'weekly',
                # last_sended должен быть меньше на 7 дней, чем текущая дата
                is_weekly_valid,
                # статус должен быть либо created либо completed
                m.status in ['created', 'completed'],
                # время начала меньше или равно текущему времени
                m.start_time.time() < now.time(),
                # время и дата  начала меньше или равно текущему времени
                m.start_time < now,
                # время и дата окончания больше или равно текущему времени
                now < m.completion_time
            ]):
                objects_list.append(m)

            elif all([
                # время и дата окончания больше или равно текущему времени
                m.frequency == 'monthly',
                # last_sended должен быть меньше на 30 дней, чем текущая дата
                is_monthly_valid,
                # статус должен быть либо created либо completed
                m.status in ['created', 'completed'],
                # время начала меньше или равно текущему времени
                m.start_time.time() < now.time(),
                # время и дата  начала меньше или равно текущему времени
                m.start_time < now,
                # время и дата окончания больше или равно текущему времени
                now < m.completion_time
            ]):
                objects_list.append(m)

        return objects_list

    def send(self):
        """  Отправляет рассылку  """

        self.status = "started"
        self.save()

        # Получение всех клиентов рассылки
        clients = self.clients.all()

        # Отправка сообщения каждому клиенту
        subject = self.message.message_subject
        message = self.message.message_text

        recipient_list = []
        for client in clients:
            recipient_list.append(client.client_email)

        try:
            count = send_mail_task(subject, message, recipient_list)
        except Exception as e:
            MailLogs.objects.create(
                mailing=self,
                last_attempt=timezone.now(),
                status="failed",
                message=f"Не удалось отправить сообщение. Ошибка: {e}"
            )
        else:
            MailLogs.objects.create(
                mailing=self,
                last_attempt=timezone.now(),
                status="success",
                message=f"Сообщений отправлено: {count}<br>"
                        f"Получателей рассылки: {len(recipient_list)}"
            )

            # Меняем текущий статус на completed и сохраняем текущее время отправки в last_sent
        self.status = 'completed'
        self.last_sent = timezone.now()
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class MailLogs(models.Model):
    last_sent = models.DateTimeField( **NULLABLE, verbose_name='дата и время последней рассылки')
    status = models.CharField(max_length=100, verbose_name='статус попытки')
    server_response = models.CharField(max_length=255, **NULLABLE, verbose_name='ответ почтового сервера')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='рассылка')

    def __str__(self):
        return {self.last_sent}

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'
