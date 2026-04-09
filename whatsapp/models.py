from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class WhatsAppSettings(models.Model):
    """Singleton — one row stores the global WhatsApp integration config."""

    enabled = models.BooleanField(
        default=False,
        verbose_name=_("Enable WhatsApp Integration"),
        help_text=_("Master switch for WhatsApp leave requests."),
    )

    class Meta:
        verbose_name = "WhatsApp Settings"

    def __str__(self):
        return "WhatsApp Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ── Conversation states ──────────────────────────────────────────────────────
STATE_IDLE = "IDLE"
STATE_MENU = "MENU"
STATE_LEAVE_TYPE = "LEAVE_TYPE"
STATE_MONTH = "MONTH"
STATE_DATES = "DATES"
STATE_CONFIRM = "CONFIRM"
STATE_BALANCE = "BALANCE"

STATE_CHOICES = [
    (STATE_IDLE, "Idle"),
    (STATE_MENU, "Menu"),
    (STATE_LEAVE_TYPE, "Choosing Leave Type"),
    (STATE_MONTH, "Choosing Month"),
    (STATE_DATES, "Entering Dates"),
    (STATE_CONFIRM, "Confirming"),
    (STATE_BALANCE, "Viewing Balance"),
]

SESSION_TIMEOUT_MINUTES = 30


class WhatsAppSession(models.Model):
    """Tracks the conversation state for each WhatsApp number."""

    phone_number = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("Phone Number"),
        help_text=_("E.164 format, e.g. +94771234567"),
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default=STATE_IDLE,
        verbose_name=_("Conversation State"),
    )
    # Stores mid-conversation data: leave_type_id, leave_type_name, month, start_day, end_day
    session_data = models.JSONField(default=dict, blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "WhatsApp Session"

    def __str__(self):
        return f"{self.phone_number} [{self.state}]"

    def is_expired(self):
        from datetime import timedelta
        return (timezone.now() - self.last_activity) > timedelta(
            minutes=SESSION_TIMEOUT_MINUTES
        )

    def reset(self):
        self.state = STATE_IDLE
        self.session_data = {}
        self.save()
