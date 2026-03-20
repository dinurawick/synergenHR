"""
Forms for PayrollRun operations
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from employee.models import Employee
from payroll.models.models import PayrollRun, Contract


class PayrollRunForm(forms.ModelForm):
    """
    Form for creating and updating PayrollRun instances
    """
    
    # Employee selection field
    selected_employees = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'employee-checkbox-list'
        }),
        required=False,
        label=_("Select Employees"),
        help_text=_("Choose employees to include in this payroll run. Leave empty to include all active employees.")
    )

    class Meta:
        model = PayrollRun
        fields = [
            'run_name',
            'run_type', 
            'frequency',
            'period_start',
            'period_end',
            'payment_date',
            'description',
            'notes',
            'selected_employees'
        ]
        widgets = {
            'run_name': forms.TextInput(attrs={
                'class': 'oh-input w-100',
                'placeholder': _('Enter payroll run name (e.g., "February 2024 - Regular")')
            }),
            'run_type': forms.Select(attrs={
                'class': 'oh-select w-100'
            }),
            'frequency': forms.Select(attrs={
                'class': 'oh-select w-100'
            }),
            'period_start': forms.DateInput(attrs={
                'type': 'date',
                'class': 'oh-input w-100'
            }),
            'period_end': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'oh-input w-100'
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'oh-input w-100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'oh-input w-100',
                'rows': 3,
                'placeholder': _('Optional description for this payroll run')
            }),
            'notes': forms.Textarea(attrs={
                'class': 'oh-input w-100', 
                'rows': 3,
                'placeholder': _('Internal notes (not visible to employees)')
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter employees by company if available
        try:
            from horilla import horilla_middlewares
            request = getattr(horilla_middlewares._thread_locals, "request", None)
            if request:
                selected_company = request.session.get("selected_company")
                if selected_company and selected_company != "all":
                    from base.models import Company
                    company = Company.find(selected_company)
                    if company:
                        self.fields["selected_employees"].queryset = Employee.objects.filter(
                            is_active=True,
                            employee_work_info__company_id=company
                        ).select_related('employee_work_info')
        except:
            pass
        
        # Enhance employee choices to show pay frequency
        employees = self.fields["selected_employees"].queryset
        enhanced_choices = []
        
        for employee in employees:
            try:
                contract = Contract.objects.filter(employee_id=employee, contract_status="active").first()
                if contract and contract.pay_frequency:
                    label = f"{employee.get_full_name()} ({contract.get_pay_frequency_display()})"
                else:
                    label = f"{employee.get_full_name()} (No pay frequency set)"
                enhanced_choices.append((employee.id, label))
            except:
                enhanced_choices.append((employee.id, employee.get_full_name()))
        
        # Update the widget choices
        self.fields["selected_employees"].choices = enhanced_choices
        
        # If editing existing payroll run, pre-select employees from notes or payslips
        if self.instance and self.instance.pk:
            # First try to get from existing payslips
            existing_employee_ids = list(self.instance.payslips.values_list('employee_id', flat=True))
            
            # If no payslips exist, try to get from notes
            if not existing_employee_ids and self.instance.notes and "Selected Employees:" in self.instance.notes:
                try:
                    notes_lines = self.instance.notes.split('\n')
                    for line in notes_lines:
                        if line.strip().startswith("Selected Employees:"):
                            ids_str = line.split("Selected Employees:")[1].strip()
                            existing_employee_ids = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
                            break
                except (ValueError, IndexError):
                    pass
            
            if existing_employee_ids:
                self.fields['selected_employees'].initial = existing_employee_ids

    def clean(self):
        cleaned_data = super().clean()
        period_start = cleaned_data.get('period_start')
        period_end = cleaned_data.get('period_end')
        payment_date = cleaned_data.get('payment_date')
        frequency = cleaned_data.get('frequency')
        selected_employees = cleaned_data.get('selected_employees')

        if period_start and period_end:
            if period_end < period_start:
                raise ValidationError({
                    'period_end': _('Period end date must be greater than or equal to period start date')
                })

        if payment_date and period_end:
            if payment_date < period_end:
                raise ValidationError({
                    'payment_date': _('Payment date should be on or after the period end date')
                })

        # Validate employee pay frequency compatibility
        if frequency and selected_employees:
            incompatible_employees = []
            for employee in selected_employees:
                try:
                    contract = Contract.objects.filter(employee_id=employee, contract_status="active").first()
                    if contract and contract.pay_frequency:
                        if not self._is_frequency_compatible(contract.pay_frequency, frequency):
                            incompatible_employees.append(f"{employee.get_full_name()} ({contract.pay_frequency})")
                except:
                    pass
            
            if incompatible_employees:
                raise ValidationError({
                    'selected_employees': _(
                        f'The following employees have incompatible pay frequencies: {", ".join(incompatible_employees)}. '
                        f'Please adjust the payroll run frequency or remove these employees.'
                    )
                })

        return cleaned_data

    def _is_frequency_compatible(self, contract_frequency, payroll_run_frequency):
        """Helper method to check frequency compatibility"""
        compatibility_matrix = {
            'weekly': ['weekly', 'bi_weekly', 'monthly', 'adhoc'],
            'semi_monthly': ['semi_monthly', 'monthly', 'adhoc'],
            'monthly': ['monthly', 'quarterly', 'annual', 'adhoc'],
        }
        
        if not contract_frequency or not payroll_run_frequency:
            return True
        
        compatible_frequencies = compatibility_matrix.get(contract_frequency, [])
        return payroll_run_frequency in compatible_frequencies

    def save(self, commit=True):
        instance = super().save(commit=commit)
        
        if commit:
            # Store selected employees for later processing
            selected_employees = self.cleaned_data.get('selected_employees')
            if hasattr(self, '_selected_employees'):
                delattr(self, '_selected_employees')
            self._selected_employees = selected_employees
            
        return instance


class PayrollRunFilterForm(forms.Form):
    """
    Form for filtering PayrollRun list view
    """
    
    run_type = forms.ChoiceField(
        choices=[('', _('All Types'))] + PayrollRun.RUN_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'oh-select'})
    )
    
    status = forms.ChoiceField(
        choices=[('', _('All Statuses'))] + PayrollRun.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'oh-select'})
    )
    
    frequency = forms.ChoiceField(
        choices=[('', _('All Frequencies'))] + PayrollRun.FREQUENCY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'oh-select'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'oh-input',
            'placeholder': _('Search by name, code, or description...')
        })
    )