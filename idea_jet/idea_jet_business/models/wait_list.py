from django.db import models
from django.utils import timezone


class Waitlist(models.Model):
    email = models.EmailField(unique=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
