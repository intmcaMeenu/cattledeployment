from django.apps import AppConfig


class CattleAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cattle_app'

    def ready(self):
        import cattle_app.signals  # This imports and connects the signals
