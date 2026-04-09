import logging
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import WhatsAppSettings
from .sender import send_whatsapp
from .state_machine import process_message

logger = logging.getLogger(__name__)


# ── Twilio Webhook ───────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def webhook(request):
    """
    Receives incoming WhatsApp messages from Twilio.
    Twilio sends a POST with 'From' and 'Body' fields.
    We process the message and reply with TwiML.
    """
    settings_obj = WhatsAppSettings.get()
    if not settings_obj.enabled:
        # Integration disabled — return empty TwiML (no reply)
        return _twiml_response("")

    from_number = request.POST.get("From", "")
    body = request.POST.get("Body", "").strip()

    if not from_number:
        return HttpResponse(status=400)

    try:
        reply = process_message(from_number, body)
    except Exception as exc:
        logger.exception("Error processing WhatsApp message from %s: %s", from_number, exc)
        reply = "⚠️ Something went wrong. Please try again later."

    return _twiml_response(reply)


def _twiml_response(message: str) -> HttpResponse:
    """Returns a minimal TwiML XML response."""
    if message:
        body_xml = f"<Body>{_xml_escape(message)}</Body>"
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{body_xml}</Message></Response>'
    else:
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    return HttpResponse(twiml, content_type="text/xml")


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )


# ── Settings Page ────────────────────────────────────────────────────────────

@login_required
def whatsapp_settings(request):
    """
    Admin settings page — toggle integration on/off,
    view connected Twilio number, manage per-employee toggles.
    """
    if not request.user.is_superuser and not request.user.has_perm(
        "whatsapp.change_whatsappsettings"
    ):
        messages.error(request, _("You do not have permission to access this page."))
        return redirect("home-page")

    settings_obj = WhatsAppSettings.get()

    if request.method == "POST":
        enabled = request.POST.get("enabled") == "on"
        settings_obj.enabled = enabled
        settings_obj.save()
        messages.success(request, _("WhatsApp settings saved."))
        return redirect("whatsapp-settings")

    # Build employee list with their mobile + whatsapp_enabled status
    from employee.models import Employee
    employees = Employee.objects.filter(
        is_active=True
    ).select_related("employee_work_info").order_by(
        "employee_first_name", "employee_last_name"
    )

    twilio_number = os.environ.get("TWILIO_WHATSAPP_NUMBER", "Not configured")
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    # Mask the SID for display
    masked_sid = (account_sid[:6] + "..." + account_sid[-4:]) if len(account_sid) > 10 else "Not configured"

    return render(request, "whatsapp/settings.html", {
        "settings_obj": settings_obj,
        "employees": employees,
        "twilio_number": twilio_number,
        "masked_sid": masked_sid,
    })


@login_required
@require_POST
def toggle_employee_whatsapp(request, employee_id):
    """Toggle WhatsApp enabled/disabled for a specific employee."""
    if not request.user.is_superuser and not request.user.has_perm(
        "whatsapp.change_whatsappsettings"
    ):
        return HttpResponse(status=403)

    from employee.models import EmployeeWorkInformation
    try:
        work_info = EmployeeWorkInformation.objects.get(employee_id=employee_id)
        work_info.whatsapp_enabled = not getattr(work_info, "whatsapp_enabled", True)
        work_info.save()
    except EmployeeWorkInformation.DoesNotExist:
        pass

    return redirect("whatsapp-settings")
