from django.urls import path
from . import views

urlpatterns = [
    path("webhook/", views.webhook, name="whatsapp-webhook"),
    path("settings/", views.whatsapp_settings, name="whatsapp-settings"),
    path(
        "toggle-employee/<int:employee_id>/",
        views.toggle_employee_whatsapp,
        name="whatsapp-toggle-employee",
    ),
]
