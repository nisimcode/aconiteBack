from aconiteBack.models import BaseModel
from django.db import models

from accounts.models import Profile


class Widget(BaseModel):
    location = models.CharField(max_length=255)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="widgets"
    )

    class Meta:
        db_table = "widgets"
        ordering = ("location", "profile__user__username")
        verbose_name = "Widget"
        verbose_name_plural = "Widgets"
