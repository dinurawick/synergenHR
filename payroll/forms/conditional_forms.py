"""
Forms for handling conditional formatting operations.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from base.forms import ModelForm
from payroll.models.models import ConditionalFormatting


class ConditionalFormattingForm(ModelForm):
    """Form for creating and updating conditional formatting rules."""

    class Meta:
        """Meta options for the form."""

        model = ConditionalFormatting
        fields = "__all__"
        exclude = ["is_active", "company_id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs: dict = self.fields["use_python_code"].widget.attrs
        self.fields["python_code"].required = False
        
        # Remove help text from fields
        self.fields["name"].help_text = ""
        self.fields["module_type"].help_text = ""
        self.fields["description"].help_text = ""
        self.fields["use_python_code"].help_text = ""
        
        attrs[
            "onchange"
        ] = """
        if($(this).is(':checked')){
            $('#oc-editor').show();
        }else{
            $('#oc-editor').hide();
        }
        """

        # Set default Python code template based on module type
        if self.instance.pk is None:
            self.instance.python_code = self.get_default_code()
        else:
            # When editing, remove these fields to prevent changes
            del self.fields["use_python_code"]
            del self.fields["python_code"]
            del self.fields["module_type"]

    def get_default_code(self):
        """Get default Python code template."""
        return '''
"""
Conditional Formatting Code

This function is called to evaluate conditions and calculate amounts.

Available variables:
- employee: Employee object
- contract: Contract object (for payroll)
- basic_pay: Basic salary amount
- start_date: Period start date
- end_date: Period end date
- attendance_days: Number of days attended (if applicable)
- overtime_hours: Overtime hours (if applicable)

Return format:
{
    'condition': True/False,  # Whether the condition is met
    'amount': 0.0,           # Calculated amount (if applicable)
    'message': ''            # Optional message
}
"""

def evaluate_condition(**kwargs):
    """
    Main evaluation function
    
    Args:
        **kwargs: All available context variables
    
    Returns:
        dict: Result with 'condition', 'amount', and optional 'message'
    """
    employee = kwargs.get('employee')
    basic_pay = kwargs.get('basic_pay', 0)
    
    # Example: Apply if basic pay > 50000
    condition_met = basic_pay > 50000
    
    # Example: Calculate 10% of basic pay
    calculated_amount = basic_pay * 0.10 if condition_met else 0
    
    return {
        'condition': condition_met,
        'amount': calculated_amount,
        'message': f'Condition evaluated for {employee}'
    }
'''
