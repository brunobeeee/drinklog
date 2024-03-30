import os

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'
        db_table = 'log'
