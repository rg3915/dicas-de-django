from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myproject.profiles'

    def ready(self):
        from django.contrib.auth.models import User
        from django.db.models.signals import post_save, pre_save

        from .signals import update_user_profile, user_pre_save_receiver

        pre_save.connect(user_pre_save_receiver, sender=User)
        post_save.connect(update_user_profile, sender=User)
