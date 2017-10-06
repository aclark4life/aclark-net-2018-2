# rock_n_roll/apps.py

from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in


class DatabaseConfig(AppConfig):
    name = 'aclarknet.database'

    def ready(self):
        from .signals import login_receiver
        # registering signals with the model's string label
        user_logged_in.connect(login_receiver)
