from django.apps import AppConfig


class WhatsappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whatsapp"

    def ready(self):
        from django.urls import include, path
        from horilla.horilla_settings import APPS
        from horilla.urls import urlpatterns

        APPS.append("whatsapp")
        urlpatterns.append(
            path("whatsapp/", include("whatsapp.urls")),
        )
        super().ready()
