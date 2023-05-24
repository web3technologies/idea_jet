from django.db import models


class BusinessModelType(models.Model):

    business_model_type = models.CharField(max_length=255)
    business_model_description = models.CharField(max_length=255)