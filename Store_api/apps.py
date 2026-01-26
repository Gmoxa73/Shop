from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Store_api'

    def ready(self):
        import Store_api.signals  # Импорт сигналов