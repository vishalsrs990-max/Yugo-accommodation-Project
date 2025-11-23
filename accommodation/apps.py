from django.apps import AppConfig


class AccommodationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accommodation"

    def ready(self):
        # import signals so post_save hooks are registered
        import accommodation.signals  # noqa
