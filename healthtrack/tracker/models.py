from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Measurement(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='measurements',
        verbose_name='Пользователь'
    )
    measured_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата и время измерения'
    )
    systolic = models.PositiveIntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(300)],
        verbose_name='Верхнее (систолическое)'
    )
    diastolic = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        verbose_name='Нижнее (диастолическое)'
    )
    pulse = models.PositiveIntegerField(
        validators=[MinValueValidator(30), MaxValueValidator(220)],
        verbose_name='Пульс'
    )
    note = models.TextField(blank=True, verbose_name='Заметка')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-measured_at']
        verbose_name = 'Измерение'
        verbose_name_plural = 'Измерения'
        indexes = [
            models.Index(fields=['user', '-measured_at']),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.systolic}/{self.diastolic} — {self.measured_at:%d.%m.%Y %H:%M}'

    @property
    def is_high(self):
        return self.systolic > 140 or self.diastolic > 90

    @property
    def is_low(self):
        return self.systolic < 90 or self.diastolic < 60

    @property
    def is_normal(self):
        return not self.is_high and not self.is_low

    @property
    def status(self):
        if self.is_high:
            return 'high'
        if self.is_low:
            return 'low'
        return 'normal'

    @property
    def status_label(self):
        return {
            'high': 'Повышено',
            'low': 'Понижено',
            'normal': 'Норма',
        }[self.status]

    @property
    def status_color(self):
        return {
            'high': 'danger',
            'low': 'warning',
            'normal': 'success',
        }[self.status]