"""
Views for handling payroll run operations.
"""

from django.contrib import messages
from django.db.models import Q, ProtectedError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from employee.models import Employee
from horilla.decorators import hx_request_required, login_required, permission_required
from payroll.forms.payroll_run_forms import PayrollRunForm, PayrollRunFilterForm
from payroll.models.models import PayrollRun, Contract


@login_required
@permission_required("payroll.view_payrollrun")
def payroll_run_list(request):
    """
    View to list all payroll runs with filtering.
    """
    runs = PayrollRun.objects.filter(is_active=True).select_related(
        "run_created_by", "approved_by", "company_id"
    )

    # Apply filters
    run_type = request.GET.get("run_type")
    status = request.GET.get("status")
    frequency = request.GET.get("frequency")
    search = request.GET.get("search")

    if run_type:
        runs = runs.filter(run_type=run_type)
    if status:
        runs = runs.filter(status=status)
    if frequency:
        runs = runs.filter(frequency=frequency)
    if search:
        runs = runs.filter(
            Q(run_name__icontains=search)
            | Q(run_code__icontains=search)
            | Q(description__icontains=search)
        )

    filter_form = PayrollRunFilterForm(request.GET)

    context = {
        "runs": runs,
        "filter_form": filter_form,
    }
    
    # If it's an HTMX request, return just the list
    if request.headers.get('HX-Request'):
        return render(request, "payroll/payroll_run/payroll_run_list.html", context)
    
    # Otherwise return the full page
    return render(request, "payroll/payroll_run/payroll_run_view_main.html", context)


@login_required
@hx_request_required
@permission_required("payroll.add_payrollrun")
def create_payroll_run(request):
    """
    View to create a new payroll run.
    """
    if request.method == "POST":
        form = PayrollRunForm(request.POST)
        if form.is_valid():
            payroll_run = form.save(commit=False)
            payroll_run.run_created_by = request.user.employee_get
            payroll_run.save()
            
            # Store selected employees for later use when status changes to approved
            selected_employees = form.cleaned_data.get('selected_employees')
            if selected_employees:
                # Store employee IDs in the payroll run for later payslip generation
                # We'll create a simple relationship or store in notes for now
                employee_ids = [str(emp.id) for emp in selected_employees]
                if payroll_run.notes:
                    payroll_run.notes += f"\n\nSelected Employees: {','.join(employee_ids)}"
                else:
                    payroll_run.notes = f"Selected Employees: {','.join(employee_ids)}"
                payroll_run.save()
                
            messages.success(request, _("Payroll run created successfully. Payslips will be generated when status is set to 'Approved'."))
            return HttpResponse("<script>window.location.reload()</script>")
        return render(request, "payroll/payroll_run/payroll_run_form.html", {"form": form})

    form = PayrollRunForm()
    return render(request, "payroll/payroll_run/payroll_run_form.html", {"form": form})


@login_required
@hx_request_required
@permission_required("payroll.change_payrollrun")
def update_payroll_run(request, run_id):
    """
    View to update a payroll run.
    """
    payroll_run = get_object_or_404(PayrollRun, id=run_id)

    # Don't allow editing if status is paid or cancelled
    if payroll_run.status in ["paid", "cancelled"]:
        messages.error(
            request,
            _(f"Cannot edit payroll run with status '{payroll_run.get_status_display()}'"),
        )
        return HttpResponse("<script>window.location.reload()</script>")

    if request.method == "POST":
        form = PayrollRunForm(request.POST, instance=payroll_run)
        if form.is_valid():
            payroll_run = form.save()
            
            # Handle employee selection updates - only store selection, don't generate payslips yet
            selected_employees = form.cleaned_data.get('selected_employees')
            if selected_employees is not None:  # Only update if employees were selected
                # Store employee IDs in notes for later payslip generation when approved
                employee_ids = [str(emp.id) for emp in selected_employees]
                
                # Update or add employee selection to notes
                notes_lines = payroll_run.notes.split('\n') if payroll_run.notes else []
                updated_notes = []
                employee_line_found = False
                
                for line in notes_lines:
                    if line.strip().startswith("Selected Employees:"):
                        # Replace existing employee selection
                        updated_notes.append(f"Selected Employees: {','.join(employee_ids)}")
                        employee_line_found = True
                    else:
                        updated_notes.append(line)
                
                if not employee_line_found:
                    # Add new employee selection
                    if updated_notes and updated_notes[-1].strip():
                        updated_notes.append("")  # Add blank line
                    updated_notes.append(f"Selected Employees: {','.join(employee_ids)}")
                
                payroll_run.notes = '\n'.join(updated_notes)
                payroll_run.save()
                
                # If payroll run is already approved, regenerate payslips
                if payroll_run.status == "approved":
                    try:
                        # Remove existing payslips for this run
                        payroll_run.payslips.all().delete()
                        
                        # Generate new payslips
                        generated_count = generate_payslips_for_approved_run(payroll_run)
                        messages.success(request, _(f"Payroll run updated and {generated_count} payslips regenerated successfully!"))
                    except Exception as e:
                        messages.error(request, _(f"Payroll run updated but error regenerating payslips: {str(e)}"))
                else:
                    messages.success(request, _("Payroll run updated successfully. Payslips will be generated when status is set to 'Approved'."))
            else:
                messages.success(request, _("Payroll run updated successfully"))
            
            return HttpResponse("<script>window.location.reload()</script>")
        return render(
            request,
            "payroll/payroll_run/payroll_run_form.html",
            {"form": form, "payroll_run": payroll_run},
        )

    form = PayrollRunForm(instance=payroll_run)
    return render(
        request,
        "payroll/payroll_run/payroll_run_form.html",
        {"form": form, "payroll_run": payroll_run},
    )


@login_required
@hx_request_required
@permission_required("payroll.view_payrollrun")
def view_payroll_run(request, run_id):
    """
    View to display payroll run details.
    """
    payroll_run = get_object_or_404(PayrollRun, id=run_id)
    payslips = payroll_run.payslips.all().select_related("employee_id")

    context = {
        "payroll_run": payroll_run,
        "payslips": payslips,
    }
    return render(request, "payroll/payroll_run/payroll_run_view.html", context)


@login_required
@hx_request_required
@permission_required("payroll.delete_payrollrun")
def delete_payroll_run(request, run_id):
    """
    View to delete a payroll run.
    """
    try:
        payroll_run = get_object_or_404(PayrollRun, id=run_id)
        
        # Don't allow deleting if status is paid
        if payroll_run.status == "paid":
            messages.error(
                request,
                _("Cannot delete a paid payroll run"),
            )
            return HttpResponse(status=400)
        
        # Check if there are payslips
        if payroll_run.payslips.exists():
            messages.error(
                request,
                _(f"Cannot delete payroll run '{payroll_run.run_name}' because it has {payroll_run.payslips.count()} payslips attached"),
            )
            return HttpResponse(status=400)
        
        run_name = payroll_run.run_name
        payroll_run.delete()
        messages.success(request, _(f"Payroll run '{run_name}' deleted successfully"))
        
    except ProtectedError:
        messages.error(
            request,
            _("Cannot delete payroll run as it is referenced by payslips"),
        )
        return HttpResponse(status=400)
    except Exception as e:
        messages.error(request, _(f"Error deleting payroll run: {str(e)}"))
        return HttpResponse(status=400)

    # Return updated list
    runs = PayrollRun.objects.filter(is_active=True).select_related(
        "run_created_by", "approved_by", "company_id"
    )
    filter_form = PayrollRunFilterForm()
    return render(
        request,
        "payroll/payroll_run/payroll_run_list.html",
        {"runs": runs, "filter_form": filter_form},
    )


@login_required
@hx_request_required
@permission_required("payroll.change_payrollrun")
def update_payroll_run_status(request, run_id):
    """
    View to update payroll run status.
    """
    if request.method == "POST":
        payroll_run = get_object_or_404(PayrollRun, id=run_id)
        new_status = request.POST.get("status")

        if new_status in dict(PayrollRun.STATUS_CHOICES):
            old_status = payroll_run.status
            payroll_run.status = new_status
            
            # Set approved_by when status changes to approved
            if new_status == "approved" and old_status != "approved":
                payroll_run.approved_by = request.user.employee_get
                
                # Generate payslips when status changes to approved
                try:
                    generated_count = generate_payslips_for_approved_run(payroll_run)
                    if generated_count > 0:
                        messages.success(
                            request,
                            _(f"Payroll run approved and {generated_count} payslips generated successfully!")
                        )
                    else:
                        messages.success(
                            request,
                            _(f"Payroll run approved. No new payslips were generated (employees may already have payslips for this period).")
                        )
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error generating payslips for payroll run {payroll_run.id}: {str(e)}")
                    messages.error(
                        request,
                        _(f"Payroll run approved but error generating payslips: {str(e)}")
                    )
            else:
                messages.success(
                    request,
                    _(f"Payroll run status updated to '{payroll_run.get_status_display()}'"),
                )
            
            payroll_run.save()
        else:
            messages.error(request, _("Invalid status"))

    return HttpResponse("<script>window.location.reload()</script>")


def generate_payslips_for_approved_run(payroll_run):
    """
    Generate payslips for employees in an approved payroll run.
    This function now considers employee contract pay frequency.
    """
    from payroll.models.models import Payslip, Contract
    from payroll.views.component_views import payroll_calculation, save_payslip, calculate_employer_contribution
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    generated_count = 0
    skipped_count = 0
    
    # Use database transaction to ensure data consistency
    with transaction.atomic():
        # Get selected employees from notes (temporary solution)
        selected_employee_ids = []
        if payroll_run.notes and "Selected Employees:" in payroll_run.notes:
            try:
                # Extract employee IDs from notes
                notes_lines = payroll_run.notes.split('\n')
                for line in notes_lines:
                    if line.strip().startswith("Selected Employees:"):
                        ids_str = line.split("Selected Employees:")[1].strip()
                        selected_employee_ids = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
                        break
            except (ValueError, IndexError):
                pass
        
        # If no employees selected in notes, get all active employees
        if not selected_employee_ids:
            from employee.models import Employee
            selected_employees = Employee.objects.filter(is_active=True)
        else:
            from employee.models import Employee
            selected_employees = Employee.objects.filter(id__in=selected_employee_ids, is_active=True)
        
        for employee in selected_employees:
            # Check employee's contract pay frequency compatibility
            contract = Contract.objects.filter(employee_id=employee, contract_status="active").first()
            
            if not contract:
                skipped_count += 1
                continue
                
            # Check if employee's pay frequency matches or is compatible with payroll run frequency
            if not is_frequency_compatible(contract.pay_frequency, payroll_run.frequency):
                skipped_count += 1
                continue
            
            # Check if payslip already exists for this employee and period
            existing_payslip = Payslip.objects.filter(
                employee_id=employee,
                start_date=payroll_run.period_start,
                end_date=payroll_run.period_end
            ).first()
            
            if not existing_payslip:
                try:
                    # Calculate salary based on payroll run frequency and contract
                    adjusted_period = calculate_pay_period_for_frequency(
                        payroll_run.period_start, 
                        payroll_run.period_end, 
                        contract.pay_frequency,
                        payroll_run.frequency
                    )
                    
                    # Generate payslip data using existing payroll calculation
                    payslip_data = payroll_calculation(employee, adjusted_period['start'], adjusted_period['end'])
                    
                    # Safely parse JSON data
                    try:
                        pay_data = json.loads(payslip_data["json_data"]) if isinstance(payslip_data["json_data"], str) else payslip_data["json_data"]
                    except (json.JSONDecodeError, TypeError) as json_error:
                        logger.error(f"JSON parsing error for employee {employee.id}: {json_error}")
                        skipped_count += 1
                        continue
                    
                    # Prepare data for saving
                    data = {
                        "employee": employee,
                        "start_date": payslip_data["start_date"],
                        "end_date": payslip_data["end_date"],
                        "status": "draft",
                        "contract_wage": payslip_data["contract_wage"],
                        "basic_pay": payslip_data["basic_pay"],
                        "gross_pay": payslip_data["gross_pay"],
                        "deduction": payslip_data["total_deductions"],
                        "net_pay": payslip_data["net_pay"],
                        "pay_data": pay_data,
                        "installments": payslip_data["installments"],
                        "payroll_run": payroll_run
                    }
                    
                    # Calculate employer contribution
                    # calculate_employer_contribution(data)  # Disabled - using new employer_contributions system
                    
                    # Save the payslip
                    payslip_instance = save_payslip(**data)
                    generated_count += 1
                    
                except Exception as e:
                    # Log the error but continue with other employees
                    logger.error(f"Error generating payslip for employee {employee.id}: {str(e)}")
                    skipped_count += 1
                    continue
            else:
                # Link existing payslip to this payroll run if not already linked
                if not existing_payslip.payroll_run:
                    existing_payslip.payroll_run = payroll_run
                    existing_payslip.save()
        
        # Update payroll run totals
        payroll_run.update_totals()
    
    return generated_count


def is_frequency_compatible(contract_frequency, payroll_run_frequency):
    """
    Check if employee's contract pay frequency is compatible with payroll run frequency.
    
    Args:
        contract_frequency: Employee's contract pay frequency (weekly, monthly, semi_monthly)
        payroll_run_frequency: Payroll run frequency (weekly, bi_weekly, semi_monthly, monthly, quarterly, annual, adhoc)
    
    Returns:
        bool: True if compatible, False otherwise
    """
    # Compatibility matrix
    compatibility_matrix = {
        # Contract frequency -> Compatible payroll run frequencies
        'weekly': ['weekly', 'bi_weekly', 'monthly', 'adhoc'],
        'semi_monthly': ['semi_monthly', 'monthly', 'adhoc'],
        'monthly': ['monthly', 'quarterly', 'annual', 'adhoc'],
    }
    
    if not contract_frequency or not payroll_run_frequency:
        return True  # Allow if either is not set (backward compatibility)
    
    compatible_frequencies = compatibility_matrix.get(contract_frequency, [])
    return payroll_run_frequency in compatible_frequencies


def calculate_pay_period_for_frequency(period_start, period_end, contract_frequency, payroll_run_frequency):
    """
    Calculate the actual pay period based on contract and payroll run frequencies.
    
    Args:
        period_start: Payroll run period start
        period_end: Payroll run period end  
        contract_frequency: Employee's contract pay frequency
        payroll_run_frequency: Payroll run frequency
    
    Returns:
        dict: {'start': adjusted_start_date, 'end': adjusted_end_date}
    """
    from datetime import timedelta
    
    # For most cases, use the payroll run period as-is
    adjusted_start = period_start
    adjusted_end = period_end
    
    # Special handling for frequency mismatches
    if contract_frequency == 'weekly' and payroll_run_frequency == 'bi_weekly':
        # For weekly employees in bi-weekly runs, calculate for 2 weeks
        pass  # Use full period
    elif contract_frequency == 'weekly' and payroll_run_frequency == 'monthly':
        # For weekly employees in monthly runs, use full month
        pass  # Use full period
    elif contract_frequency == 'semi_monthly' and payroll_run_frequency == 'monthly':
        # For semi-monthly employees in monthly runs, use full month
        pass  # Use full period
    
    return {
        'start': adjusted_start,
        'end': adjusted_end
    }
