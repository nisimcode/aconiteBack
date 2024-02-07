from django.contrib.postgres import fields
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class Cluster(BaseModel):
    clues = fields.ArrayField(models.CharField(max_length=255), size=4)
    answer = models.CharField(max_length=255)

    def __str__(self):
        return self.answer

    class Meta:
        db_table = "clusters"
        ordering = ("answer", "clues")
