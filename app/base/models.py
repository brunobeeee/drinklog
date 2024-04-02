import os

from django.db import models
from django.contrib.auth.models import User

class Log(models.Model):
    user = models.ForeignKey(User,
        on_delete=models.CASCADE,
        null=os.environ.get("ALLOW_NULL_USERS"),
        blank=os.environ.get("ALLOW_BLANK_USERS"))
    date = models.DateField(auto_now_add=True)
    intensity = models.IntegerField(default=0)
    overdrive = models.BooleanField(default=False)

    def __str__(self):
        return str(self.date) + " | " + str(self.intensity) + " | " + str(self.overdrive)

    class Meta:
        ordering = ['date']
        order_with_respect_to = 'user'
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        db_table = 'log'

class Task(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        order_with_respect_to = 'user'
