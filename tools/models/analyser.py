from django.db import models
from .base import TimeStampedModel

class SchoolProfileScan(TimeStampedModel):
    slug = models.CharField(max_length=255)
    score = models.PositiveIntegerField(blank=True, null=True)
    analysis = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.slug} - {self.score}"
