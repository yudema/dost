from django.db import models
from django.utils import timezone

class Transport(models.Model):
    STATUS_CHOICES = [
        ('loading', 'В загрузке'),
        ('in_transit', 'В пути'),
        ('customs', 'На таможне'),
        ('delivered', 'Доставлен'),
        ('delayed', 'Задержка'),
        ('cancelled', 'Отменен')
    ]

    number = models.CharField(max_length=20, unique=True, verbose_name='Номер транспорта')
    type = models.CharField(max_length=50, verbose_name='Тип транспорта')
    capacity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Грузоподъемность')
    current_location = models.CharField(max_length=200, verbose_name='Текущее местоположение')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='loading', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Транспорт'
        verbose_name_plural = 'Транспорт'

    def __str__(self):
        return f"{self.number} - {self.get_status_display()}"

class Cargo(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='cargoes', verbose_name='Транспорт')
    description = models.TextField(verbose_name='Описание груза')
    weight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Вес')
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Объем')
    sender = models.CharField(max_length=200, verbose_name='Отправитель')
    receiver = models.CharField(max_length=200, verbose_name='Получатель')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Груз'
        verbose_name_plural = 'Грузы'

    def __str__(self):
        return f"Груз для {self.transport.number}"

class TransportStatus(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='status_history', verbose_name='Транспорт')
    status = models.CharField(max_length=20, choices=Transport.STATUS_CHOICES, verbose_name='Статус')
    location = models.CharField(max_length=200, verbose_name='Местоположение')
    timestamp = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True, verbose_name='Комментарий')

    class Meta:
        verbose_name = 'История статуса'
        verbose_name_plural = 'История статусов'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transport.number} - {self.get_status_display()}"

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решен'),
        ('closed', 'Закрыт'),
    ]

    session_id = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    transport = models.ForeignKey(Transport, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} ({self.email})"

    class Meta:
        verbose_name = 'Тикет'
        verbose_name_plural = 'Тикеты'

class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    is_staff = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'Сотрудник' if self.is_staff else 'Клиент'}: {self.message[:50]}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['created_at']
