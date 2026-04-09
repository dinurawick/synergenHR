"""
This module provides Horilla ModelForms for creating and managing leave-related data,
including leave type, leave request, leave allocation request, holidays and company leaves.
"""

import re
import uuid
from datetime import date, datetime
from typing import Any

from django import forms
from django.apps import apps
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.widgets import TextInput
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from base.forms import ModelForm as BaseModelForm
from base.methods import filtersubordinatesemployeemodel, reload_queryset
from employee.filters import EmployeeFilter
from employee.forms import MultipleFileField
from employee.models import Employee
from horilla import horilla_middlewares
from horilla_widgets.forms import HorillaForm, HorillaModelForm
from horilla_widgets.widgets.horilla_multi_select_field import HorillaMultiSelectField
from horilla_widgets.widgets.select_widgets import HorillaMultiSelectWidget
from leave.methods import get_leave_day_attendance
from leave.models import (
    AvailableLeave,
    LeaveAllocationRequest,
    LeaveallocationrequestComment,
    LeaveRequest,
    LeaverequestComment,
    LeaverequestFile,
    LeaveType,
    RestrictLeave,
)

CHOICES = [("yes", _("Yes")), ("no", _("No"))]
LEAVE_MAX_LIMIT = 1e5


class ConditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = getattr(horilla_middlewares._thread_locals, "request", None)
        reload_queryset(self.fields)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Select,)):
                field.widget.attrs["style"] = (
                    "width:100%; height:50px;border: 1px solid hsl(213deg,22%,84%);border-radius: 0rem;padding: 0.8rem 1.25rem;"
                )
            elif isinstance(widget, forms.DateInput):
                field.initial = date.today
                widget.input_type = "date"
                widget.format = "%Y-%m-%d"
                field.input_formats = ["%Y-%m-%d"]

            elif isinstance(
                widget, (forms.NumberInput, forms.EmailInput, forms.TextInput)
            ):
                field.widget.attrs.update(
                    {"class": "oh-input w-100", "placeholder": field.label}
                )
            elif isinstance(widget, (forms.Textarea)):
                field.widget.attrs.update(
                    {
                        "class": "oh-input w-100",
                        "placeholder": field.label,
                        "rows": 2,
                        "cols": 40,
                    }
                )
            elif isinstance(
                widget,
                (
                    forms.CheckboxInput,
                    forms.CheckboxSelectMultiple,
                ),
            ):
                field.widget.attrs.update({"class": "oh-switch__checkbox"})
        try:
            self.fields["employee_id"].initial = request.user.employee_get
        except:
            pass

        try:
            self.fields["company_id"].initial = request.user.employee_get.get_company
        except:
            pass


class LeaveTypeAdminForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = "__all__"
        exclude = ["conditional_formatting_rule", "use_conditional_formatting", "gender_restriction"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if f := self.fields.get("company_id"):
            from horilla_widgets.forms import default_select_option_template

            w = getattr(f.widget, "widget", f.widget)
            if isinstance(w, forms.Select):
                w.option_template_name = default_select_option_template


class LeaveTypeForm(ConditionForm):

    employee_id = forms.ModelMultipleChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'oh-select oh-select-2 w-100',
            'size': '10',
            'style': 'min-height: 200px;'
        }),
        label=_("Employee"),
        required=False,
    )

    class Meta:
        model = LeaveType
        fields = "__all__"
        exclude = ["is_active"]
        labels = {
            "name": _("Name"),
        }
        widgets = {
            "color": TextInput(attrs={"type": "color", "style": "height:40px;"}),
            "period_in": forms.HiddenInput(),
            "total_days": forms.HiddenInput(),
            "require_approval": forms.Select(attrs={"id": "id_require_approval"}),
            "require_attachment": forms.Select(attrs={"id": "id_require_attachment"}),
            "exclude_company_leave": forms.Select(attrs={"id": "id_exclude_company_leave"}),
            "exclude_holiday": forms.Select(attrs={"id": "id_exclude_holiday"}),
            "exclude_weekends": forms.Select(attrs={"id": "id_exclude_weekends"}),
            "gender_restriction": forms.Select(attrs={
                "id": "id_gender_restriction", 
                "class": "oh-select oh-select-2 w-100",
                "style": "background-color: white !important; color: black !important;"
            }),
            "monthly_recurring": forms.CheckboxInput(attrs={"class": "oh-switch__checkbox"}),
            "recurring_carry_forward": forms.CheckboxInput(attrs={"class": "oh-switch__checkbox"}),
            "prorate_on_confirmation": forms.CheckboxInput(attrs={"class": "oh-switch__checkbox"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if "employee_id" in self.errors:
            del self.errors["employee_id"]
        if "exceed_days" in self.errors:
            del self.errors["exceed_days"]
        
        # If conditional formatting is enabled, Total Days is not required
        use_conditional_formatting = cleaned_data.get("use_conditional_formatting", False)
        if use_conditional_formatting:
            # Remove count field errors since it's not required with conditional formatting
            if "count" in self.errors:
                del self.errors["count"]
            # Set a default value for total_days (will be overridden by conditional formatting)
            cleaned_data["total_days"] = 0
        
        if not cleaned_data.get("limit_leave"):
            cleaned_data["total_days"] = LEAVE_MAX_LIMIT
            cleaned_data["reset"] = True
            cleaned_data["reset_based"] = "yearly"
            cleaned_data["reset_month"] = "1"
            cleaned_data["reset_day"] = "1"

        return cleaned_data

    def save(self, *args, **kwargs):
        # Save the leave type first
        leave_type = super().save(*args, **kwargs)
        
        # Handle employee assignments
        if employees := self.data.getlist("employee_id"):
            for employee_id in employees:
                employee = Employee.objects.get(id=employee_id)
                AvailableLeave(
                    leave_type_id=leave_type,
                    employee_id=employee,
                    available_days=leave_type.total_days,
                ).save()
        
        return leave_type

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add conditional formatting dropdown dynamically
        try:
            from payroll.models.models import ConditionalFormatting
            from django.forms import ModelChoiceField
            
            self.fields["conditional_formatting_rule"] = ModelChoiceField(
                queryset=ConditionalFormatting.objects.filter(
                    module_type="leave",
                    is_active=True,
                ),
                required=False,
                label=_("Conditional Formatting Rule"),
                help_text=_("Select a conditional formatting rule to apply"),
                widget=forms.Select(attrs={
                    "id": "id_conditional_formatting_rule",
                    "class": "oh-select oh-select-2 w-100"
                })
            )
        except ImportError:
            pass
        
        # Add widget attributes for conditional formatting toggle
        if "use_conditional_formatting" in self.fields:
            self.fields["use_conditional_formatting"].widget.attrs.update({
                "id": "id_use_conditional_formatting",
                "onchange": "toggleConditionalFormattingDropdown($(this))",
                "class": "oh-switch__checkbox"
            })
        
        # Filter employees based on gender restriction from POST data or instance
        gender_restriction = None
        if self.data.get("gender_restriction"):
            gender_restriction = self.data.get("gender_restriction")
        elif self.instance and self.instance.pk and self.instance.gender_restriction:
            gender_restriction = self.instance.gender_restriction
        
        # Apply gender-based filtering to employee queryset
        if gender_restriction and gender_restriction in ['male', 'female', 'other']:
            # Filter employees by gender - this sets the initial queryset
            filtered_employees = Employee.objects.filter(gender=gender_restriction, is_active=True)
            self.fields["employee_id"].queryset = filtered_employees
            # Store gender restriction in widget for filter to use
            self.fields["employee_id"].widget.attrs['data-gender'] = gender_restriction
        else:
            # No gender restriction - show all active employees
            self.fields["employee_id"].queryset = Employee.objects.filter(is_active=True)




class UpdateLeaveTypeForm(ConditionForm):

    def __init__(self, *args, **kwargs):
        super(UpdateLeaveTypeForm, self).__init__(*args, **kwargs)

        empty_fields = []
        for field_name, field_value in self.instance.__dict__.items():
            if field_value is None or field_value == "":
                if field_name.endswith("_id"):
                    foreign_key_field_name = re.sub("_id$", "", field_name)
                    empty_fields.append(foreign_key_field_name)
                empty_fields.append(field_name)

        for index, visible in enumerate(self.visible_fields()):
            if list(self.fields.keys())[index] in empty_fields:
                visible.field.widget.attrs["style"] = (
                    "display:none;width:100%; height:50px;border: 1px solid hsl(213deg,22%,84%);border-radius: 0rem;padding: 0.8rem 1.25rem;"
                )
                visible.field.widget.attrs["data-hidden"] = True

        if expire_date := self.instance.carryforward_expire_date:
            self.fields["carryforward_expire_date"] = expire_date
        
        # Add conditional formatting dropdown dynamically to avoid app loading order issues
        try:
            from payroll.models.models import ConditionalFormatting
            from django.forms import ModelChoiceField
            
            # Get initial value from instance if it exists
            initial_value = None
            if self.instance and hasattr(self.instance, 'conditional_formatting_rule') and self.instance.conditional_formatting_rule:
                initial_value = self.instance.conditional_formatting_rule
            
            self.fields["conditional_formatting_rule"] = ModelChoiceField(
                queryset=ConditionalFormatting.objects.filter(
                    module_type="leave",
                    is_active=True,
                ),
                required=False,
                initial=initial_value,
                label=_("Conditional Formatting Rule"),
                help_text=_("Select a conditional formatting rule to apply"),
                widget=forms.Select(attrs={
                    "id": "id_conditional_formatting_rule",
                    "class": "oh-select oh-select-2 w-100"
                })
            )
        except ImportError:
            pass
        
        # Add widget attributes for conditional formatting toggle
        if "use_conditional_formatting" in self.fields:
            self.fields["use_conditional_formatting"].widget.attrs.update({
                "id": "id_use_conditional_formatting",
                "onchange": "toggleConditionalFormattingDropdown($(this))",
                "class": "oh-switch__checkbox"
            })
        
        # Add widget attributes for gender restriction with onchange event
        if "gender_restriction" in self.fields:
            self.fields["gender_restriction"].widget.attrs.update({
                "id": "id_gender_restriction",
                "class": "oh-select oh-select-2 w-100",
                "onchange": "filterEmployeesByGender($(this))"
            })
        
        # Filter employees based on gender restriction from POST data or instance
        gender_restriction = None
        if self.data.get("gender_restriction"):
            gender_restriction = self.data.get("gender_restriction")
        elif self.instance and self.instance.pk and self.instance.gender_restriction:
            gender_restriction = self.instance.gender_restriction
        
        # Apply gender-based filtering to employee queryset (for update form)
        if gender_restriction and gender_restriction in ['male', 'female', 'other']:
            # Filter employees by gender
            filtered_employees = Employee.objects.filter(gender=gender_restriction, is_active=True)
            # Note: UpdateLeaveTypeForm doesn't have employee_id field, but we keep this for consistency
            # The filtering will be applied in the assign leave functionality
            pass

    class Meta:
        model = LeaveType
        fields = [
            'icon', 'name', 'color', 'payment', 'count', 'period_in', 'limit_leave',
            'total_days', 'reset', 'is_encashable', 'reset_based', 'reset_month',
            'reset_day', 'reset_weekend', 'carryforward_type', 'carryforward_max',
            'carryforward_expire_in', 'carryforward_expire_period', 'carryforward_expire_date',
            'require_approval', 'require_attachment', 'exclude_company_leave',
            'exclude_holiday', 'exclude_weekends', 'is_compensatory_leave',
            'monthly_recurring',
            'recurring_carry_forward',
            'prorate_on_confirmation',
            'use_conditional_formatting', 'conditional_formatting_rule', 'gender_restriction', 'company_id'
        ]
        widgets = {
            "color": TextInput(attrs={"type": "color", "style": "height:40px;"}),
            "period_in": forms.HiddenInput(),
            "total_days": forms.HiddenInput(),
            "require_approval": forms.Select(attrs={"id": "id_require_approval"}),
            "require_attachment": forms.Select(attrs={"id": "id_require_attachment"}),
            "exclude_company_leave": forms.Select(attrs={"id": "id_exclude_company_leave"}),
            "exclude_holiday": forms.Select(attrs={"id": "id_exclude_holiday"}),
            "exclude_weekends": forms.Select(attrs={"id": "id_exclude_weekends"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if "exceed_days" in self.errors:
            del self.errors["exceed_days"]
        if not cleaned_data["limit_leave"]:
            cleaned_data["total_days"] = LEAVE_MAX_LIMIT
            cleaned_data["reset"] = True
            cleaned_data["reset_based"] = "yearly"
            cleaned_data["reset_month"] = "1"
            cleaned_data["reset_day"] = "1"

        return cleaned_data

    def save(self, *args, **kwargs):
        # Save conditional_formatting_rule if it was provided
        if 'conditional_formatting_rule' in self.cleaned_data:
            self.instance.conditional_formatting_rule = self.cleaned_data['conditional_formatting_rule']
        leave_type = super().save(*args, **kwargs)
        return leave_type


class LeaveRequestCreationForm(BaseModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["attachment"].widget.attrs["accept"] = ".jpg, .jpeg, .png, .pdf"
        self.fields["leave_type_id"].widget.attrs.update(
            {
                "hx-include": "#leaveRequestCreateForm",
                "hx-target": "#availableLeaveCount",
                "hx-swap": "outerHTML",
                "hx-trigger": "change",
                "hx-get": "/leave/employee-available-leave-count",
            }
        )
        self.fields["employee_id"].widget.attrs.update(
            {
                "hx-target": "#id_leave_type_id_parent_div",
                "hx-trigger": "change",
                "hx-get": "/leave/get-employee-leave-types?form=LeaveRequestCreationForm",
            }
        )
        self.fields["start_date"].widget.attrs.update(
            {
                "hx-include": "#leaveRequestCreateForm",
                "hx-target": "#availableLeaveCount",
                "hx-swap": "outerHTML",
                "hx-trigger": "change",
                "hx-get": "/leave/employee-available-leave-count",
            }
        )
        
        # Filter cover employees to same department
        if self.instance and self.instance.employee_id_id:
            employee = self.instance.employee_id
            if hasattr(employee, 'employee_work_info') and employee.employee_work_info.department_id:
                department = employee.employee_work_info.department_id
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    employee_work_info__department_id=department,
                    is_active=True
                ).exclude(id=employee.id)
            else:
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    is_active=True
                ).exclude(id=employee.id)
        else:
            self.fields["cover_employee_id"].queryset = Employee.objects.filter(is_active=True)

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("horilla_form.html", context)
        return table_html

    class Meta:
        model = LeaveRequest
        fields = [
            "employee_id",
            "leave_type_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "cover_employee_id",
            "attachment",
            "description",
        ]


class LeaveRequestUpdationForm(BaseModelForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        leave_request = self.instance
        employee = leave_request.employee_id
        leave_type = leave_request.leave_type_id

        if employee:
            available_leaves = employee.available_leave.all()
            assigned_leave_types = LeaveType.objects.filter(
                id__in=available_leaves.values_list("leave_type_id", flat=True)
            )

            if leave_type and leave_type.id not in assigned_leave_types.values_list(
                "id", flat=True
            ):
                assigned_leave_types |= LeaveType.objects.filter(id=leave_type.id)

            self.fields["leave_type_id"].queryset = assigned_leave_types
            
            # Filter cover employees to same department
            if hasattr(employee, 'employee_work_info') and employee.employee_work_info.department_id:
                department = employee.employee_work_info.department_id
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    employee_work_info__department_id=department,
                    is_active=True
                ).exclude(id=employee.id)
            else:
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    is_active=True
                ).exclude(id=employee.id)

        self.fields["leave_type_id"].widget.attrs.update(
            {
                "hx-include": "#leaveRequestUpdateForm",
                "hx-target": "#assinedLeaveAvailableCount",
                "hx-swap": "outerHTML",
                "hx-trigger": "change",
                "hx-get": "/leave/employee-available-leave-count",
            }
        )
        self.fields["employee_id"].widget.attrs.update(
            {
                "hx-target": "#id_leave_type_id_parent_div",
                "hx-trigger": "change",
                "hx-get": "/leave/get-employee-leave-types?form=LeaveRequestUpdationForm",
            }
        )
        self.fields["attachment"].widget.attrs["accept"] = ".jpg, .jpeg, .png, .pdf"

        self.fields["start_date"].widget.attrs.update(
            {
                "hx-include": "#leaveRequestUpdateForm",
                "hx-target": "#assinedLeaveAvailableCount",
                "hx-swap": "outerHTML",
                "hx-trigger": "change",
                "hx-get": "/leave/employee-available-leave-count",
            }
        )

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("horilla_form.html", context)
        return table_html

    class Meta:
        model = LeaveRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "cover_employee_id",
            "attachment",
            "description",
        ]


class AvailableLeaveForm(BaseModelForm):
    """
    Form for managing available leave data.

    This form allows users to manage available leave data by specifying details such as
    the leave type and employee.

    Attributes:
        - leave_type_id: A ModelChoiceField representing the leave type associated with the available leave.
        - employee_id: A ModelChoiceField representing the employee associated with the available leave.
    """

    leave_type_id = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.SelectMultiple,
        empty_label=None,
    )
    employee_id = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.SelectMultiple,
        empty_label=None,
    )

    class Meta:
        model = AvailableLeave
        fields = ["leave_type_id", "employee_id", "is_active"]


class LeaveOneAssignForm(HorillaModelForm):
    """
    Form for assigning available leave to employees.

    This form allows administrators to assign available leave to a single employee
    by specifying the employee and setting the is_active flag.

    Attributes:
        - employee_id: A HorillaMultiSelectField representing the employee to assign leave to.
    """

    employee_id = HorillaMultiSelectField(
        queryset=Employee.objects.all(),
        widget=HorillaMultiSelectWidget(
            filter_route_name="employee-widget-filter",
            filter_class=EmployeeFilter,
            filter_instance_contex_name="f",
            filter_template_path="employee_filters.html",
            required=True,
        ),
        label="Employee",
    )

    class Meta:
        """
        Meta class for additional options
        """

        model = AvailableLeave
        fields = ["employee_id", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.fields)


class AvailableLeaveUpdateForm(BaseModelForm):
    """
    Form for updating available leave data.

    This form allows users to update available leave data by modifying fields such as
    available_days, carryforward_days, and is_active.

    Attributes:
        - Meta: Inner class defining metadata options.
            - model: The model associated with the form (AvailableLeave).
            - fields: A list of fields to include in the form.
    """

    class Meta:
        """
        Meta class for additional options
        """

        model = AvailableLeave
        fields = ["available_days", "carryforward_days", "is_active"]


class UserLeaveRequestForm(BaseModelForm):
    description = forms.CharField(label=_("Description"), widget=forms.Textarea)
    attachment = forms.FileField(label=_("Attachment"), required=False)

    def __init__(self, *args, **kwargs):
        leave_type = kwargs.pop("initial", None)
        employee = kwargs.pop("employee", None)
        super(UserLeaveRequestForm, self).__init__(*args, **kwargs)
        self.fields["attachment"].widget.attrs["accept"] = ".jpg, .jpeg, .png, .pdf"
        if employee:
            available_leaves = employee.available_leave.all()
            assigned_leave_types = LeaveType.objects.filter(
                id__in=available_leaves.values_list("leave_type_id", flat=True)
            )
            self.fields["leave_type_id"].queryset = assigned_leave_types
            
            # Filter cover employees to same department
            if hasattr(employee, 'employee_work_info') and employee.employee_work_info.department_id:
                department = employee.employee_work_info.department_id
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    employee_work_info__department_id=department,
                    is_active=True
                ).exclude(id=employee.id)
            else:
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    is_active=True
                ).exclude(id=employee.id)
        
        if leave_type:
            self.fields["leave_type_id"].queryset = LeaveType.objects.filter(
                id=leave_type["leave_type_id"].id
            )
            self.fields["leave_type_id"].initial = leave_type["leave_type_id"].id
            self.fields["leave_type_id"].empty_label = None

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("horilla_form.html", context)
        return table_html

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveRequest
        fields = [
            "employee_id",
            "leave_type_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "cover_employee_id",
            "attachment",
            "description",
        ]
        widgets = {
            "employee_id": forms.HiddenInput(),
        }


excluded_fields = [
    "id",
    "approved_available_days",
    "approved_carryforward_days",
    "created_at",
    "attachment",
]


class AvailableLeaveColumnExportForm(forms.Form):
    """
    Form for selecting columns to export in available leave data.

    This form allows users to select specific columns from the AvailableLeave model
    for export. The available columns are dynamically generated based on the
    model's meta information, excluding specified excluded_fields.

    Attributes:
        - model_fields: A list of fields in the AvailableLeave model.
        - field_choices: A list of field choices for the form, consisting of field names
          and their verbose names, excluding specified excluded_fields.
        - selected_fields: A MultipleChoiceField representing the selected columns
          to be exported.
    """

    model_fields = AvailableLeave._meta.get_fields()
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_fields
        if hasattr(field, "verbose_name") and field.name not in excluded_fields
    ]
    selected_fields = forms.MultipleChoiceField(
        choices=field_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "employee_id",
            "leave_type_id",
            "available_days",
            "carryforward_days",
            "total_leave_days",
        ],
    )


class RejectForm(forms.Form):
    """
    Form for rejecting a leave request.

    This form allows administrators to provide a rejection reason when rejecting
    a leave request.

    Attributes:
        - reason: A CharField representing the reason for rejecting the leave request.
    """

    reason = forms.CharField(
        label=_("Rejection Reason"),
        widget=forms.Textarea(attrs={"rows": 4, "class": "p-4 oh-input w-100"}),
    )

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveRequest
        fields = ["reject_reason"]


class UserLeaveRequestCreationForm(BaseModelForm):

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("horilla_form.html", context)
        return table_html

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        employee = cleaned_data.get("employee_id")
        if start_date and end_date and employee:
            overlapping = LeaveRequest.objects.filter(
                employee_id=employee,
                start_date__lte=end_date,
                end_date__gte=start_date,
            ).exclude(status__in=["cancelled", "rejected"])
            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise forms.ValidationError(
                    _("You already have a leave request for this date range.")
                )
        return cleaned_data

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop("employee", None)
        super().__init__(*args, **kwargs)
        self.fields["attachment"].widget.attrs["accept"] = ".jpg, .jpeg, .png, .pdf"
        if employee:
            available_leaves = employee.available_leave.all()
            assigned_leave_types = LeaveType.objects.filter(
                id__in=available_leaves.values_list("leave_type_id", flat=True)
            )
            self.fields["leave_type_id"].queryset = assigned_leave_types
            
            # Filter cover employees to same department
            if hasattr(employee, 'employee_work_info') and employee.employee_work_info.department_id:
                department = employee.employee_work_info.department_id
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    employee_work_info__department_id=department,
                    is_active=True
                ).exclude(id=employee.id)
            else:
                self.fields["cover_employee_id"].queryset = Employee.objects.filter(
                    is_active=True
                ).exclude(id=employee.id)
        
        self.fields["leave_type_id"].widget.attrs.update(
            {
                "hx-include": "#userLeaveForm",
                "hx-target": "#availableLeaveCount",
                "hx-swap": "outerHTML",
                "hx-trigger": "change",
                "hx-get": f"/leave/employee-available-leave-count",
            }
        )
        self.fields["employee_id"].initial = employee

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "cover_employee_id",
            "attachment",
            "description",
            "requested_days",
        ]
        widgets = {
            "employee_id": forms.HiddenInput(),
            "requested_days": forms.HiddenInput(),
        }


class LeaveAllocationRequestForm(BaseModelForm):
    """
    Form for creating a leave allocation request.

    This form allows users to create a leave allocation request by specifying
    details such as leave type, employee, requested days, description, and attachment.

    Methods:
        - as_p: Render the form fields as HTML table rows with Bootstrap styling.
    """

    def as_p(self, *args, **kwargs):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("horilla_form.html", context)
        return table_html

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveAllocationRequest
        fields = [
            "leave_type_id",
            "employee_id",
            "requested_days",
            "description",
            "attachment",
        ]


class LeaveAllocationRequestRejectForm(forms.Form):
    """
    Form for rejecting a leave allocation request.

    This form allows administrators to provide a rejection reason when rejecting
    a leave allocation request.

    Attributes:
        - reason: A CharField representing the reason for rejecting the leave allocation request.
    """

    reason = forms.CharField(
        label=_("Rejection Reason"),
        widget=forms.Textarea(attrs={"rows": 4, "class": "p-4 oh-input w-100"}),
    )

    class Meta:
        model = LeaveAllocationRequest
        fields = ["reject_reason"]


class LeaveRequestExportForm(forms.Form):
    """
    Form for selecting fields to export in a leave request export.

    This form allows users to select specific fields from the LeaveRequest model
    for export. The available fields are dynamically generated based on the
    model's meta information, excluding certain fields specified in 'excluded_fields'.

    Attributes:
        - model_fields: A list of fields in the LeaveRequest model.
        - field_choices: A list of field choices for the form, consisting of field names
          and their verbose names, excluding specified excluded_fields.
        - selected_fields: A MultipleChoiceField representing the selected fields
          to be exported.
    """

    model_fields = LeaveRequest._meta.get_fields()
    field_choices = [
        (field.name, field.verbose_name)
        for field in model_fields
        if hasattr(field, "verbose_name") and field.name not in excluded_fields
    ]

    selected_fields = forms.MultipleChoiceField(
        choices=field_choices,
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "employee_id",
            "leave_type_Assignid",
            "start_date",
            "start_date_breakdown",
            "end_date",
            "end_date_breakdown",
            "requested_days",
            "description",
            "status",
        ],
    )


class AssignLeaveForm(HorillaForm):
    """
    Form for Payslip
    """

    leave_type_id = forms.ModelChoiceField(
        queryset=LeaveType.objects.all(),
        widget=forms.SelectMultiple(
            attrs={"class": "oh-select oh-select-2 mb-2", "required": True}
        ),
        empty_label=None,
        label=_("Leave Type"),
        required=False,
    )
    employee_id = HorillaMultiSelectField(
        queryset=Employee.objects.all(),
        widget=HorillaMultiSelectWidget(
            filter_route_name="employee-widget-filter",
            filter_class=EmployeeFilter,
            filter_instance_contex_name="f",
            filter_template_path="employee_filters.html",
            required=True,
        ),
        label=_("Employee"),
    )

    def clean(self):
        cleaned_data = super().clean()
        employee_id = cleaned_data.get("employee_id")
        leave_type_id = cleaned_data.get("leave_type_id")

        if not employee_id:
            raise forms.ValidationError({"employee_id": "This field is required"})
        if not leave_type_id:
            raise forms.ValidationError({"leave_type_id": "This field is required"})
        
        # Validate gender restriction for selected leave type
        if leave_type_id and employee_id:
            gender_restriction = leave_type_id.gender_restriction
            if gender_restriction and gender_restriction != 'all':
                # Check if any selected employee doesn't match the gender restriction
                invalid_employees = []
                for employee in employee_id:
                    if employee.gender != gender_restriction:
                        invalid_employees.append(str(employee))
                
                if invalid_employees:
                    raise forms.ValidationError({
                        "employee_id": _(f"The selected leave type '{leave_type_id.name}' is restricted to {gender_restriction} employees only. "
                                       f"The following employees do not match: {', '.join(invalid_employees)}")
                    })
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        reload_queryset(self.fields)
        self.fields["employee_id"].widget.attrs.update(
            {"required": True, "id": uuid.uuid4()}
        ),
        self.fields["leave_type_id"].label = "Leave Type"
        
        # Add onchange event to leave type to filter employees by gender restriction
        self.fields["leave_type_id"].widget.attrs.update({
            "onchange": "filterEmployeesByLeaveTypeGender($(this))"
        })


class LeaverequestcommentForm(BaseModelForm):
    """
    LeaverequestComment form
    """

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaverequestComment
        fields = ("comment",)


class LeaveCommentForm(BaseModelForm):
    """
    Leave request comment model form
    """

    verbose_name = "Add Comment"

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaverequestComment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["files"] = MultipleFileField(label="files")
        self.fields["files"].widget.attrs["accept"] = ".jpg, .jpeg, .png, .pdf"

        self.fields["files"].required = False

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html

    def save(self, commit: bool = ...) -> Any:
        multiple_files_ids = []
        files = None
        if self.files.getlist("files"):
            files = self.files.getlist("files")
            self.instance.attachemnt = files[0]
            multiple_files_ids = []
            for attachemnt in files:
                file_instance = LeaverequestFile()
                file_instance.file = attachemnt
                file_instance.save()
                multiple_files_ids.append(file_instance.pk)
        instance = super().save(commit)
        if commit:
            instance.files.add(*multiple_files_ids)
        return instance, files


class LeaveallocationrequestcommentForm(BaseModelForm):
    """
    Leave Allocation Requestcomment form
    """

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveallocationrequestComment
        fields = ("comment",)


class LeaveAllocationCommentForm(BaseModelForm):
    """
    Leave request comment model form
    """

    verbose_name = "Add Comment"

    class Meta:
        """
        Meta class for additional options
        """

        model = LeaveallocationrequestComment
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["files"] = MultipleFileField(label="files")
        self.fields["files"].required = False

    def as_p(self):
        """
        Render the form fields as HTML table rows with Bootstrap styling.
        """
        context = {"form": self}
        table_html = render_to_string("common_form.html", context)
        return table_html

    def save(self, commit: bool = ...) -> Any:
        multiple_files_ids = []
        files = None
        if self.files.getlist("files"):
            files = self.files.getlist("files")
            self.instance.attachemnt = files[0]
            multiple_files_ids = []
            for attachemnt in files:
                file_instance = LeaverequestFile()
                file_instance.file = attachemnt
                file_instance.save()
                multiple_files_ids.append(file_instance.pk)
        instance = super().save(commit)
        if commit:
            instance.files.add(*multiple_files_ids)
        return instance, files


class RestrictLeaveForm(BaseModelForm):
    def clean_end_date(self):
        start_date = self.cleaned_data.get("start_date")
        end_date = self.cleaned_data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                _("End date should not be earlier than the start date.")
            )

        return end_date

    class Meta:
        model = RestrictLeave
        fields = "__all__"
        exclude = ["is_active"]

    def __init__(self, *args, **kwargs):
        super(RestrictLeaveForm, self).__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["autocomplete"] = "title"
        self.fields["department"].widget.attrs.update(
            {
                "hx-include": "#leaveRestrictForm",
                "hx-target": "#restrictLeaveJobPosition",
                "hx-trigger": "change",
                "hx-get": "/leave/get-restrict-job-positions",
            }
        )


if apps.is_installed("attendance"):
    from .models import CompensatoryLeaveRequest, CompensatoryLeaverequestComment

    class CompensatoryLeaveForm(BaseModelForm):
        """
        Form for creating a leave allocation request.

        This form allows users to create a leave allocation request by specifying
        details such as leave type, employee, requested days, description, and attachment.

        Methods:
            - as_p: Render the form fields as HTML table rows with Bootstrap styling.
        """

        class Meta:
            """
            Meta class for additional options
            """

            attendance_id = forms.MultipleChoiceField(required=True)
            model = CompensatoryLeaveRequest
            fields = [
                # "leave_type_id",
                "employee_id",
                "attendance_id",
                # "requested_days",
                "description",
            ]

        def __init__(self, *args, **kwargs):
            super(CompensatoryLeaveForm, self).__init__(*args, **kwargs)

            request = getattr(horilla_middlewares._thread_locals, "request", None)
            instance_id = None
            if self.instance:
                instance_id = self.instance.id
            if (
                request
                and hasattr(request, "user")
                and hasattr(request.user, "employee_get")
            ):
                employee = request.user.employee_get
                holiday_attendance = get_leave_day_attendance(
                    employee, comp_id=instance_id
                )
                # Get a list of tuples containing (id, attendance_date)
                attendance_dates = list(
                    holiday_attendance.values_list("id", "attendance_date")
                )
                # Set the queryset of attendance_id to the attendance_dates
                self.fields["attendance_id"].choices = attendance_dates
            queryset = (
                filtersubordinatesemployeemodel(
                    request, Employee.objects.filter(is_active=True)
                )
                | Employee.objects.filter(employee_user_id=request.user)
            ).distinct()
            self.fields["employee_id"].queryset = queryset
            self.fields["employee_id"].widget.attrs.update(
                {
                    "hx-target": "#id_attendance_id_parent_div",
                    "hx-trigger": "change",
                    "hx-get": "/leave/get-leave-attendance-dates",
                }
            )

        def as_p(self, *args, **kwargs):
            """
            Render the form fields as HTML table rows with Bootstrap styling.
            """
            context = {"form": self}
            table_html = render_to_string("horilla_form.html", context)
            return table_html

        def clean(self):
            cleaned_data = super().clean()
            attendance_id = cleaned_data.get("attendance_id")
            if attendance_id is None or len(attendance_id) < 1:
                raise forms.ValidationError(
                    {"attendance_id": _("This field is required.")}
                )
            employee = cleaned_data.get("employee_id")
            attendance_repeat = False
            instance_id = None
            if self.instance:
                instance_id = self.instance.id
            for attendance in attendance_id:
                if (
                    CompensatoryLeaveRequest.objects.filter(
                        employee_id=employee, attendance_id=attendance
                    )
                    .exclude(Q(id=instance_id) | Q(status="rejected"))
                    .exists()
                ):
                    attendance_repeat = True
                    break
            if attendance_repeat:
                raise forms.ValidationError(
                    {
                        "attendance_id": "This attendance is already converted to complimentory leave"
                    }
                )
            return cleaned_data

    class CompensatoryLeaveRequestRejectForm(forms.Form):
        """
        Form for rejecting a compensatory leave request.

        This form allows administrators to provide a rejection reason when rejecting
        a compensatory leave request.

        Attributes:
            - reason: A CharField representing the reason for rejecting the  compensatory leave request.
        """

        reason = forms.CharField(
            label=_("Rejection Reason"),
            widget=forms.Textarea(attrs={"rows": 4, "class": "p-4 oh-input w-100"}),
        )

        class Meta:
            model = CompensatoryLeaveRequest
            fields = ["reject_reason"]

    class CompensatoryLeaveRequestcommentForm(BaseModelForm):
        """
        LeaverequestComment form
        """

        class Meta:
            """
            Meta class for additional options
            """

            model = CompensatoryLeaverequestComment
            fields = ("comment",)


class LeavePlanForm(ConditionForm):
    """
    Form for creating/updating a leave plan.
    Leave type is filtered to only types assigned to the employee.
    """

    class Meta:
        model = apps.get_model("leave", "LeavePlan")
        fields = ["leave_type_id", "start_date", "end_date", "note"]

    def __init__(self, *args, employee=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee = employee
        if employee:
            assigned_types = AvailableLeave.objects.filter(
                employee_id=employee
            ).values_list("leave_type_id", flat=True)
            self.fields["leave_type_id"].queryset = LeaveType.objects.filter(
                id__in=assigned_types
            )
        self.fields["leave_type_id"].label = _("Leave Type")
        self.fields["start_date"].label = _("Start Date")
        self.fields["end_date"].label = _("End Date")
        self.fields["note"].label = _("Note")
        self.fields["note"].required = False

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_date")
        end = cleaned_data.get("end_date")
        leave_type = cleaned_data.get("leave_type_id")

        if start and end and end < start:
            raise forms.ValidationError(_("End date cannot be before start date."))

        # Validate requested days don't exceed the employee's available balance
        if start and end and leave_type and self.employee:
            requested_days = (end - start).days + 1
            try:
                available_leave = AvailableLeave.objects.get(
                    employee_id=self.employee,
                    leave_type_id=leave_type,
                )
                total_available = available_leave.total_leave_days
                if requested_days > total_available:
                    raise forms.ValidationError(
                        _(
                            "You only have %(available)s day(s) available for %(leave_type)s, "
                            "but requested %(requested)s day(s)."
                        ) % {
                            "available": total_available,
                            "leave_type": leave_type.name,
                            "requested": requested_days,
                        }
                    )
            except AvailableLeave.DoesNotExist:
                raise forms.ValidationError(
                    _("No leave balance found for %(leave_type)s.") % {"leave_type": leave_type.name}
                )

        return cleaned_data


class LeavePlanRejectForm(forms.Form):
    """Form for rejecting a leave plan with an optional reason."""
    reject_reason = forms.CharField(
        label=_("Rejection Reason"),
        required=False,
        widget=forms.Textarea(attrs={"class": "oh-input w-100", "rows": 3}),
    )
