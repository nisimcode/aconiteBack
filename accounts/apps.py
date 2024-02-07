from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        from .tasks import kill_old_deactivated_users

        scheduler = BackgroundScheduler()

        # Add your jobs here, e.g.:
        scheduler.add_job(kill_old_deactivated_users, 'interval', days=1)

        scheduler.start()
