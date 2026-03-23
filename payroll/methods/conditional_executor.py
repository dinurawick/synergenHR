"""
conditional_executor.py

Module for executing conditional formatting rules
"""

import logging
from typing import Dict, Any, Optional

from payroll.models.models import ConditionalFormatting

logger = logging.getLogger(__name__)


def execute_individual_rule(rule, context):
    """
    Execute a specific conditional formatting rule.
    
    Args:
        rule: ConditionalFormatting instance
        context: Dictionary containing all available variables for the code
    
    Returns:
        Dict with 'condition', 'amount', and 'message' keys, or None if error
    """
    try:
        if not rule or not rule.python_code or not rule.use_python_code:
            logger.warning(f"Rule validation failed: rule={rule}, has_code={bool(rule.python_code if rule else False)}, use_python={bool(rule.use_python_code if rule else False)}")
            return None
        
        logger.info(f"Executing rule: {rule.name}, context keys: {context.keys()}")
        
        # Prepare the code for execution
        code = rule.python_code
        
        # Replace print statements to prevent output
        code = code.replace("print(", "pass_print(")
        
        # Add a dummy print function
        pass_print_func = """
def pass_print(*args, **kwargs):
    return None
"""
        code = pass_print_func + code
        
        # Execute the code
        local_vars = {}
        exec(code, {}, local_vars)
        
        # Call the evaluate_condition function with context
        if 'evaluate_condition' in local_vars:
            result = local_vars['evaluate_condition'](**context)
            logger.info(f"Rule result: {result}")
            
            # Validate result format
            if isinstance(result, dict) and 'condition' in result and 'amount' in result:
                return {
                    'condition': bool(result.get('condition', False)),
                    'amount': float(result.get('amount', 0)),
                    'message': str(result.get('message', ''))
                }
            else:
                logger.warning(
                    f"Conditional formatting rule '{rule.name}' returned invalid format: {result}"
                )
                return None
        else:
            logger.warning(
                f"Conditional formatting rule '{rule.name}' missing evaluate_condition function"
            )
            return None
            
    except Exception as e:
        logger.error(f"Error executing conditional formatting rule '{rule.name}': {e}", exc_info=True)
        return None


def execute_conditional_formatting(
    module_type: str,
    context: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Execute conditional formatting rules for a given module type.
    
    Args:
        module_type: 'payroll' or 'leave'
        context: Dictionary containing all available variables for the code
                 (employee, basic_pay, contract, etc.)
    
    Returns:
        Dict with 'condition', 'amount', and 'message' keys, or None if no active rule
    """
    try:
        # Get active conditional formatting rule for this module
        rule = ConditionalFormatting.objects.filter(
            module_type=module_type,
            is_active=True,
            use_python_code=True
        ).first()
        
        if not rule or not rule.python_code:
            return None
        
        # Prepare the code for execution
        code = rule.python_code
        
        # Replace print statements to prevent output
        code = code.replace("print(", "pass_print(")
        
        # Add a dummy print function
        pass_print_func = """
def pass_print(*args, **kwargs):
    return None
"""
        code = pass_print_func + code
        
        # Execute the code
        local_vars = {}
        exec(code, {}, local_vars)
        
        # Call the evaluate_condition function with context
        if 'evaluate_condition' in local_vars:
            result = local_vars['evaluate_condition'](**context)
            
            # Validate result format
            if isinstance(result, dict) and 'condition' in result and 'amount' in result:
                return {
                    'condition': bool(result.get('condition', False)),
                    'amount': float(result.get('amount', 0)),
                    'message': str(result.get('message', ''))
                }
            else:
                logger.warning(
                    f"Conditional formatting rule '{rule.name}' returned invalid format"
                )
                return None
        else:
            logger.warning(
                f"Conditional formatting rule '{rule.name}' missing evaluate_condition function"
            )
            return None
            
    except Exception as e:
        logger.error(f"Error executing conditional formatting: {e}")
        return None


def apply_to_allowance(employee, basic_pay, contract, start_date, end_date, **kwargs):
    """
    Apply conditional formatting to allowance calculation.
    
    Returns:
        Tuple of (should_apply: bool, calculated_amount: float, message: str)
    """
    context = {
        'employee': employee,
        'basic_pay': basic_pay,
        'contract': contract,
        'start_date': start_date,
        'end_date': end_date,
        **kwargs  # Additional context like attendance_days, overtime_hours, etc.
    }
    
    result = execute_conditional_formatting('payroll_earnings', context)
    
    if result:
        return (
            result['condition'],
            result['amount'],
            result['message']
        )
    
    # Default: no conditional formatting applied
    return (True, 0, '')


def apply_to_deduction(employee, basic_pay, contract, start_date, end_date, **kwargs):
    """
    Apply conditional formatting to deduction calculation.
    
    Returns:
        Tuple of (should_apply: bool, calculated_amount: float, message: str)
    """
    context = {
        'employee': employee,
        'basic_pay': basic_pay,
        'contract': contract,
        'start_date': start_date,
        'end_date': end_date,
        **kwargs  # Additional context like late_arrivals, etc.
    }
    
    result = execute_conditional_formatting('payroll_deductions', context)
    
    if result:
        return (
            result['condition'],
            result['amount'],
            result['message']
        )
    
    # Default: no conditional formatting applied
    return (True, 0, '')


def apply_to_leave(employee, contract, leave_type, **kwargs):
    """
    Apply conditional formatting to leave eligibility.
    
    Returns:
        Tuple of (is_eligible: bool, entitled_days: float, message: str)
    """
    context = {
        'employee': employee,
        'contract': contract,
        'leave_type': leave_type,
        **kwargs  # Additional context like months_worked, etc.
    }
    
    result = execute_conditional_formatting('leave', context)
    
    if result:
        return (
            result['condition'],
            result['amount'],  # In leave context, amount = days
            result['message']
        )
    
    # Default: no conditional formatting applied
    return (True, 0, '')
