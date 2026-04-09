"""
WhatsApp leave bot — state machine.

Each handle_* function receives the session + cleaned message text,
updates the session state/data, and returns the reply string.
"""
import calendar
import contextlib
import logging
from datetime import date

from django.utils import timezone

from .models import (
    STATE_BALANCE,
    STATE_CONFIRM,
    STATE_DATES,
    STATE_IDLE,
    STATE_LEAVE_TYPE,
    STATE_MENU,
    STATE_MONTH,
    WhatsAppSession,
)

logger = logging.getLogger(__name__)

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ── Entry point ──────────────────────────────────────────────────────────────

def process_message(phone_number: str, message_text: str) -> str:
    """
    Main entry point. Looks up (or creates) the session for this number,
    checks for timeout, then routes to the correct state handler.
    Returns the reply string to send back.
    """
    from employee.models import Employee, EmployeeWorkInformation

    # Normalise input
    text = message_text.strip()

    # Find employee by mobile number
    employee = _find_employee(phone_number)
    if employee is None:
        return (
            "❌ Your number is not registered in the HR system.\n"
            "Please contact HR to link your WhatsApp number to your employee profile."
        )

    # Check WhatsApp is enabled for this employee
    work_info = getattr(employee, "employee_work_info", None)
    if work_info and not getattr(work_info, "whatsapp_enabled", True):
        return "WhatsApp HR features are disabled for your account. Contact HR to enable."

    # Get or create session
    session, _ = WhatsAppSession.objects.get_or_create(phone_number=phone_number)

    # Reset expired sessions
    if session.state != STATE_IDLE and session.is_expired():
        session.reset()

    # Route
    state = session.state
    if state == STATE_IDLE:
        return _handle_idle(session, employee, text)
    elif state == STATE_MENU:
        return _handle_menu(session, employee, text)
    elif state == STATE_LEAVE_TYPE:
        return _handle_leave_type(session, employee, text)
    elif state == STATE_MONTH:
        return _handle_month(session, employee, text)
    elif state == STATE_DATES:
        return _handle_dates(session, employee, text)
    elif state == STATE_CONFIRM:
        return _handle_confirm(session, employee, text)
    elif state == STATE_BALANCE:
        return _handle_balance_reply(session, employee, text)
    else:
        session.reset()
        return _handle_idle(session, employee, text)


# ── State handlers ───────────────────────────────────────────────────────────

def _handle_idle(session, employee, text):
    first_name = employee.employee_first_name
    reply = (
        f"Hello {first_name}! 👋\n\n"
        "What would you like to do?\n"
        "1. Apply for Leave\n"
        "2. Check Leave Balance\n\n"
        "Reply with 1 or 2."
    )
    session.state = STATE_MENU
    session.session_data = {}
    session.save()
    return reply


def _handle_menu(session, employee, text):
    if text == "1":
        return _start_leave_type(session, employee)
    elif text == "2":
        return _show_balance(session, employee)
    else:
        return (
            "Please reply with:\n"
            "1 — Apply for Leave\n"
            "2 — Check Leave Balance"
        )


def _start_leave_type(session, employee):
    from leave.models import AvailableLeave
    balances = AvailableLeave.objects.filter(
        employee_id=employee
    ).select_related("leave_type_id").order_by("leave_type_id__name")

    if not balances.exists():
        session.reset()
        return "You have no leave types assigned. Please contact HR."

    lines = ["Your available leave types:\n"]
    leave_list = []
    for i, bal in enumerate(balances, 1):
        lines.append(f"{i}. {bal.leave_type_id.name} - {bal.total_leave_days} days")
        leave_list.append({
            "id": bal.leave_type_id.id,
            "name": bal.leave_type_id.name,
            "total": float(bal.total_leave_days),
        })
    lines.append("\nReply with the number of your choice.")

    session.state = STATE_LEAVE_TYPE
    session.session_data = {"leave_list": leave_list}
    session.save()
    return "\n".join(lines)


def _handle_leave_type(session, employee, text):
    leave_list = session.session_data.get("leave_list", [])
    try:
        idx = int(text) - 1
        if idx < 0 or idx >= len(leave_list):
            raise ValueError
    except (ValueError, TypeError):
        return (
            f"Please reply with a number between 1 and {len(leave_list)}."
        )

    chosen = leave_list[idx]
    session.session_data["leave_type_id"] = chosen["id"]
    session.session_data["leave_type_name"] = chosen["name"]
    session.session_data["leave_balance"] = chosen["total"]
    session.state = STATE_MONTH
    session.save()

    return (
        f"*{chosen['name']}* selected ✅\n\n"
        "Which month?\n"
        "1-Jan   2-Feb   3-Mar\n"
        "4-Apr   5-May   6-Jun\n"
        "7-Jul   8-Aug   9-Sep\n"
        "10-Oct  11-Nov  12-Dec\n\n"
        "Reply with the month number."
    )


def _handle_month(session, employee, text):
    try:
        month = int(text)
        if month < 1 or month > 12:
            raise ValueError
    except (ValueError, TypeError):
        return "Please reply with a month number between 1 and 12."

    month_name = MONTH_NAMES[month]
    year = date.today().year
    days_in_month = calendar.monthrange(year, month)[1]

    session.session_data["month"] = month
    session.session_data["month_name"] = month_name
    session.session_data["year"] = year
    session.state = STATE_DATES
    session.save()

    return (
        f"*{month_name} {year}* — enter your leave dates as start-end\n"
        f"e.g. *13-16* for {month_name} 13 to {month_name} 16\n"
        f"(Month has {days_in_month} days)"
    )


def _handle_dates(session, employee, text):
    data = session.session_data
    month = data.get("month")
    year = data.get("year")
    month_name = data.get("month_name")
    days_in_month = calendar.monthrange(year, month)[1]

    # Parse "13-16" or "13" (single day)
    try:
        parts = text.split("-")
        if len(parts) == 1:
            start_day = end_day = int(parts[0])
        elif len(parts) == 2:
            start_day = int(parts[0])
            end_day = int(parts[1])
        else:
            raise ValueError

        if not (1 <= start_day <= days_in_month and 1 <= end_day <= days_in_month):
            raise ValueError
        if start_day > end_day:
            raise ValueError

    except (ValueError, TypeError):
        return (
            f"Invalid dates. Please enter as start-end, e.g. *13-16*\n"
            f"{month_name} has {days_in_month} days."
        )

    # Calculate days and check balance
    num_days = end_day - start_day + 1
    balance = data.get("leave_balance", 0)
    balance_after = round(balance - num_days, 1)

    if num_days > balance:
        excess = round(num_days - balance, 1)
        return (
            f"❌ You've exceeded your balance by *{excess} day{'s' if excess != 1 else ''}*.\n\n"
            f"📋 {data['leave_type_name']}: *{balance} days* available\n"
            f"📅 You requested: *{num_days} days* ({month_name} {start_day}–{end_day})\n\n"
            "Please enter a shorter date range."
        )

    session.session_data["start_day"] = start_day
    session.session_data["end_day"] = end_day
    session.session_data["num_days"] = num_days
    session.session_data["balance_after"] = balance_after
    session.state = STATE_CONFIRM
    session.save()

    start_date = date(year, month, start_day)
    end_date = date(year, month, end_day)

    return (
        f"Please confirm your leave request:\n\n"
        f"📋 *{data['leave_type_name']}*\n"
        f"📅 {month_name} {start_day} – {month_name} {end_day} ({num_days} day{'s' if num_days > 1 else ''})\n"
        f"💰 Balance after approval: *{balance_after} days*\n\n"
        "Reply *YES* to submit or *NO* to cancel."
    )


def _handle_confirm(session, employee, text):
    upper = text.upper().strip()

    if upper == "NO":
        session.reset()
        return "❌ Cancelled. Reply anything to start over."

    if upper != "YES":
        return "Please reply *YES* to confirm or *NO* to cancel."

    # Create the LeaveRequest
    data = session.session_data
    try:
        leave_request = _create_leave_request(employee, data)
    except Exception as exc:
        logger.exception("Failed to create leave request from WhatsApp: %s", exc)
        session.reset()
        return (
            "⚠️ Something went wrong creating your leave request. "
            "Please try again or contact HR."
        )

    session.reset()
    return (
        f"✅ Leave request submitted! (#{leave_request.id})\n\n"
        f"📋 {data['leave_type_name']}\n"
        f"📅 {data['month_name']} {data['start_day']} – {data['month_name']} {data['end_day']}\n\n"
        "Your manager will review it shortly. "
        "You'll receive a WhatsApp message once it's approved or rejected."
    )


def _show_balance(session, employee):
    from leave.models import AvailableLeave
    balances = AvailableLeave.objects.filter(
        employee_id=employee
    ).select_related("leave_type_id").order_by("leave_type_id__name")

    if not balances.exists():
        session.reset()
        return "You have no leave types assigned. Please contact HR."

    lines = ["📊 *Your Leave Balances:*\n"]
    for bal in balances:
        lines.append(
            f"📋 {bal.leave_type_id.name}: *{bal.total_leave_days} days*"
        )
    lines.append("\nReply anything to start over.")

    session.reset()
    return "\n".join(lines)


def _handle_balance_reply(session, employee, text):
    session.reset()
    return _handle_idle(session, employee, text)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _find_employee(phone_number: str):
    """
    Match the incoming WhatsApp number to an employee.
    Checks work_info.mobile first, then employee.phone (personal phone).
    """
    from employee.models import Employee, EmployeeWorkInformation

    number = phone_number.replace("whatsapp:", "").strip()

    # 1. Try work info mobile exact match
    work_info = EmployeeWorkInformation.objects.filter(mobile=number).first()
    if work_info:
        return work_info.employee_id

    # 2. Try personal phone exact match
    employee = Employee.objects.filter(phone=number, is_active=True).first()
    if employee:
        return employee

    # 3. Fuzzy last-9-digits match (handles country code variations)
    if len(number.lstrip("+")) >= 9:
        suffix = number.lstrip("+")[-9:]
        work_info = EmployeeWorkInformation.objects.filter(
            mobile__endswith=suffix
        ).first()
        if work_info:
            return work_info.employee_id

        employee = Employee.objects.filter(
            phone__endswith=suffix, is_active=True
        ).first()
        if employee:
            return employee

    return None


def _create_leave_request(employee, data: dict):
    """Creates an approved-pending LeaveRequest from confirmed session data."""
    from leave.models import AvailableLeave, LeaveRequest, LeaveType

    leave_type = LeaveType.objects.get(id=data["leave_type_id"])
    start_date = date(data["year"], data["month"], data["start_day"])
    end_date = date(data["year"], data["month"], data["end_day"])
    requested_days = data["num_days"]

    leave_request = LeaveRequest.objects.create(
        employee_id=employee,
        leave_type_id=leave_type,
        start_date=start_date,
        end_date=end_date,
        requested_days=requested_days,
        description="Submitted via WhatsApp.",
        status="requested",
    )
    return leave_request
