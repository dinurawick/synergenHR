import calendar
import datetime as dt
import sys
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from dateutil.relativedelta import relativedelta


def leave_reset():
    from leave.models import LeaveType

    today = datetime.now()
    today_date = today.date()
    leave_types = LeaveType.objects.filter(reset=True)
    # Looping through filtered leave types with reset is true
    for leave_type in leave_types:
        # Looping through all available leaves
        available_leaves = leave_type.employee_available_leave.all()

        for available_leave in available_leaves:
            reset_date = available_leave.reset_date
            expired_date = available_leave.expired_date
            if reset_date == today_date:
                available_leave.update_carryforward()
                # new_reset_date = available_leave.set_reset_date(assigned_date=today_date,available_leave = available_leave)
                new_reset_date = available_leave.set_reset_date(
                    assigned_date=today_date, available_leave=available_leave
                )
                available_leave.reset_date = new_reset_date
                available_leave.save()
            if expired_date and expired_date <= today_date:
                new_expired_date = available_leave.set_expired_date(
                    available_leave=available_leave, assigned_date=today_date
                )
                available_leave.expired_date = new_expired_date
                available_leave.save()

        if (
            leave_type.carryforward_expire_date
            and leave_type.carryforward_expire_date <= today_date
        ):
            leave_type.carryforward_expire_date = leave_type.set_expired_date(
                today_date
            )
            leave_type.save()


def monthly_recurring_leave_credit():
    """
    Credits leave days monthly for all leave types with monthly_recurring=True.
    Runs daily; credits on the 1st of each month only.
    Respects recurring_carry_forward: if disabled, resets to total_days instead of adding.
    """
    from leave.models import AvailableLeave, LeaveType

    today = datetime.now().date()
    if today.day != 1:
        return

    recurring_leave_types = LeaveType.objects.filter(monthly_recurring=True)
    for leave_type in recurring_leave_types:
        available_leaves = leave_type.employee_available_leave.all()
        for available_leave in available_leaves:
            if leave_type.recurring_carry_forward:
                # Carry forward unused days — just add the monthly allocation
                available_leave.available_days = round(
                    available_leave.available_days + leave_type.total_days, 3
                )
            else:
                # No carry forward — reset to the monthly allocation
                available_leave.available_days = leave_type.total_days
            available_leave.save()


if not any(
    cmd in sys.argv
    for cmd in ["makemigrations", "migrate", "compilemessages", "flush", "shell"]
):
    """
    Initializes and starts background tasks using APScheduler when the server is running.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(leave_reset, "interval", seconds=20)
    scheduler.add_job(monthly_recurring_leave_credit, "interval", hours=24)

    scheduler.start()
