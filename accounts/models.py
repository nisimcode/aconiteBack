from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .roles import ROLES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(choices=ROLES, default="user", max_length=255)
    is_banned = models.BooleanField(default=False)
    banned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deactivated = models.BooleanField(default=False)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to add custom logic before saving the instance.
        """
        # Check if the instance is already in the database
        if self.pk:
            old_instance = Profile.objects.get(pk=self.pk)
            # Update banned_at if the banned status has changed
            if self.is_banned != old_instance.is_banned:
                self.banned_at = timezone.now()

        # # Update deactivated_at based on is_active status
        # if self.is_deactivated and not self.deactivated_at:
        #     self.deactivated_at = timezone.now()
        # elif not self.is_deactivated and self.deactivated_at:
        #     self.deactivated_at = None

        # Call the parent class's save method
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        """
        Return the username of the user.
        """
        return self.user.username

    class Meta:
        db_table = "profiles"
        ordering = ("created_at", "updated_at")


class DeadProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="dead_profiles")
    died_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dead_profiles"
        ordering = ("died_at", "user__username")
        verbose_name = "Dead Profile"
        verbose_name_plural = "Dead Profiles"

    def __str__(self):
        """
        Return the username of the user.
        """
        return self.user.username, self.died_at


class UserDeadProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_dead_profiles")
    dead_profile = models.ForeignKey(DeadProfile, on_delete=models.CASCADE, related_name="user_dead_profiles")

    class Meta:
        db_table = "user_dead_profiles"
        ordering = ("user", "dead_profile")
        verbose_name = "User Dead Profile"
        verbose_name_plural = "User Dead Profiles"

    def __str__(self):
        """
        Return the username of the user.
        """
        return self.user.username
