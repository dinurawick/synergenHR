# leave/signals.py

import threading

from django.apps import apps
from django.db.models.signals import post_migrate, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from horilla.methods import get_horilla_model_class
from leave.models import LeaveRequest

if apps.is_installed("attendance"):

    @receiver(post_save, sender=LeaveRequest)
    def leaverequest_pre_save(sender, instance, **_kwargs):
        """
        Overriding LeaveRequest model save method
        """
        WorkRecords = get_horilla_model_class(
            app_label="attendance", model="workrecords"
        )
        if (
            instance.start_date == instance.end_date
            and instance.end_date_breakdown != instance.start_date_breakdown
        ):
            instance.end_date_breakdown = instance.start_date_breakdown
            super(LeaveRequest, instance).save()

        period_dates = instance.requested_dates()
        if instance.status == "approved":
            for date in period_dates:
                try:
                    work_entry = (
                        WorkRecords.objects.filter(
                            date=date,
                            employee_id=instance.employee_id,
                        ).first()
                        if WorkRecords.objects.filter(
                            date=date,
                            employee_id=instance.employee_id,
                        ).exists()
                        else WorkRecords()
                    )
                    work_entry.employee_id = instance.employee_id
                    work_entry.is_leave_record = True
                    work_entry.leave_request_id = instance
                    work_entry.day_percentage = (
                        0.50
                        if instance.start_date == date
                        and instance.start_date_breakdown == "first_half"
                        or instance.end_date == date
                        and instance.end_date_breakdown == "second_half"
                        else 0.00
                    )
                    status = (
                        "CONF"
                        if instance.start_date == date
                        and instance.start_date_breakdown == "first_half"
                        or instance.end_date == date
                        and instance.end_date_breakdown == "second_half"
                        else "ABS"
                    )
                    work_entry.work_record_type = status
                    work_entry.date = date
                    work_entry.message = (
                        "Leave"
                        if status == "ABS"
                        else _("Half day Attendance need to validate")
                    )
                    work_entry.save()

                except Exception as e:
                    print(e)

        else:
            for date in period_dates:
                WorkRecords.objects.filter(
                    is_leave_record=True,
                    date=date,
                    employee_id=instance.employee_id,
                ).delete()

    @receiver(pre_delete, sender=LeaveRequest)
    def leaverequest_pre_delete(sender, instance, **kwargs):
        from attendance.models import WorkRecords

        work_records = WorkRecords.objects.filter(leave_request_id=instance).delete()


# @receiver(post_migrate)
def add_missing_leave_to_workrecords(sender, **kwargs):
    if sender.label not in ["attendance", "leave"]:
        return

    if not apps.is_installed("attendance"):
        return
    try:
        from attendance.models import WorkRecords
        from leave.models import LeaveRequest

        work_records = WorkRecords.objects.filter(
            is_leave_record=True, leave_request_id__isnull=True
        )
        if not work_records.exists():
            return

        leave_requests = LeaveRequest.objects.all()
        date_leave_map = {}

        for leave in leave_requests:
            for date in leave.requested_dates():
                key = (leave.employee_id, date)
                date_leave_map[key] = leave

        records_to_update = []
        for record in work_records:
            leave_request = date_leave_map.get((record.employee_id, record.date))
            if leave_request:
                record.leave_request_id = leave_request
                records_to_update.append(record)

        if records_to_update:
            WorkRecords.objects.bulk_update(
                records_to_update, ["leave_request_id"], batch_size=500
            )
            print(
                f"Successfully updated {len(records_to_update)} work records with leave information"
            )

    except Exception as e:
        print(f"Error in leave/work records sync: {e}")


# ── WhatsApp approval/rejection notifications ────────────────────────────────

@receiver(post_save, sender=LeaveRequest)
def notify_employee_via_whatsapp(sender, instance, created, **kwargs):
    """
    When a LeaveRequest transitions to 'approved' or 'rejected',
    send a WhatsApp message to the employee if integration is enabled.
    """
    import contextlib
    import threading

    if created:
        return  # Only notify on status changes, not creation

    if instance.status not in ("approved", "rejected", "cancelled"):
        return

    def _send():
        with contextlib.suppress(Exception):
            from whatsapp.models import WhatsAppSettings
            settings_obj = WhatsAppSettings.get()
            if not settings_obj.enabled:
                return

            employee = instance.employee_id
            work_info = getattr(employee, "employee_work_info", None)
            mobile = (work_info.mobile if work_info and work_info.mobile else None) or employee.phone
            if not mobile:
                return
            if not getattr(work_info, "whatsapp_enabled", True) if work_info else False:
                return

            from whatsapp.sender import send_whatsapp

            leave_type = str(instance.leave_type_id)
            start = instance.start_date.strftime("%d %b %Y")
            end = (instance.end_date or instance.start_date).strftime("%d %b %Y")

            if instance.status == "approved":
                msg = (
                    f"✅ Your leave request has been approved!\n\n"
                    f"📋 {leave_type}\n"
                    f"📅 {start} – {end}\n\n"
                    "Enjoy your time off! 🎉"
                )
            elif instance.status in ("rejected", "cancelled"):
                reason = instance.reject_reason or ""
                msg = (
                    f"❌ Your leave request was not approved.\n\n"
                    f"📋 {leave_type}\n"
                    f"📅 {start} – {end}\n"
                    + (f"📝 Reason: {reason}\n" if reason else "")
                    + "\nContact HR if you have questions."
                )
            else:
                return

            send_whatsapp(mobile, msg)

    threading.Thread(target=_send, daemon=True).start()
