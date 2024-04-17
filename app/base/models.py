import os

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Log(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=os.environ.get("ALLOW_NULL_USERS"),
        blank=os.environ.get("ALLOW_BLANK_USERS"),
    )
    date = models.DateField()
    intensity = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    overdrive = models.BooleanField(default=False)

    def __str__(self):
        return (
            str(self.date) + " | " + str(self.intensity) + " | " + str(self.overdrive)
        )

    class Meta:
        order_with_respect_to = "user"
