from django.conf import settings
from django.db import models

from .models_user import User  # noqa: F401


class Course(models.Model):
    TYPE_QUALIFICATION = 'qualification'
    TYPE_RETRAINING = 'retraining'
    TYPE_SAFETY = 'safety'

    TYPE_CHOICES = [
        (TYPE_QUALIFICATION, 'Повышение квалификации'),
        (TYPE_RETRAINING, 'Переподготовка'),
        (TYPE_SAFETY, 'Охрана труда'),
    ]

    title = models.CharField('Название', max_length=200)
    course_type = models.CharField('Вид курса', max_length=20, choices=TYPE_CHOICES)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['course_type', 'title']

    def __str__(self):
        return f'{self.get_course_type_display()} — {self.title}'


class Application(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'Идет обучение'),
        (STATUS_COMPLETED, 'Обучение завершено'),
    ]

    PAYMENT_QR = 'qr'
    PAYMENT_MIR = 'mir'
    PAYMENT_OFFICE = 'office'

    PAYMENT_CHOICES = [
        (PAYMENT_QR, 'Предоплата по QR-коду'),
        (PAYMENT_MIR, 'Оплата картой МИР'),
        (PAYMENT_OFFICE, 'Постоплата в офисе организации'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Пользователь',
    )
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='Курс')
    start_date = models.DateField('Дата начала обучения')
    payment_method = models.CharField(
        'Способ оплаты', max_length=20, choices=PAYMENT_CHOICES
    )
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW
    )
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заявка #{self.pk} — {self.user.username}'

    def can_leave_review(self):
        return self.status != self.STATUS_NEW


class Review(models.Model):
    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Заявка',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField('Отзыв')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Отзыв к заявке #{self.application_id}'
