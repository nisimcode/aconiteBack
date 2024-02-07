import logging
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from .models import Profile, DeadProfile

logger = logging.getLogger(__name__)


def kill_old_deactivated_users():
    logger.info("Running kill_old_deactivated_users task...")
    # thirty_days_ago = timezone.now() - timedelta(days=30)
    wait_period = timezone.now() - timedelta(seconds=15)  # 15 seconds
    old_deactivated_profiles = Profile.objects.filter(deactivated_at__lt=wait_period)
    for old_profile in old_deactivated_profiles:
        try:
            old_profile = Profile.objects.get(id=old_profile.id)
            dead_profile = DeadProfile.objects.create(user=old_profile.user)
            logger.info(f"Created DeadProfile with id {dead_profile.id}")
            if dead_profile.id:  # Check if the save operation succeeded
                old_profile.user.is_active = False
                old_profile.user.save()
                logger.info(f"Deleting Profile with id {old_profile.id}")
                old_profile.delete()
        except ObjectDoesNotExist:
            logger.error(f"Profile with id {old_profile.id} does not exist")
