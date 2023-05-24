from django.db import models



class IndustryType(models.Model):

    industry_type = models.CharField(max_length=255)
    industry_description = models.CharField(max_length=255)