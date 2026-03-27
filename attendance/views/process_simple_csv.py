"""
process_simple_csv.py

This module handles the transformation of simple CSV attendance format
(employee_id, in_date, in_time, out_date, out_time) to the system's expected format.
"""

from datetime import datetime, timedelta
import pandas as pd
from django.utils.translation import gettext_lazy as _

from base.models import EmployeeShift, WorkType
from employee.models import Employee


def calculate_worked_hours(in_date, in_time, out_date, out_time):
    """
    Calculate worked hours from in/out datetime strings.
    
    Args:
        in_date (str): Check-in date (YYYY-MM-DD)
        in_time (str): Check-in time (HH:MM:SS)
        out_date (str): Check-out date (YYYY-MM-DD) 
        out_time (str): Check-out time (HH:MM:SS)
        
    Returns:
        str: Worked hours in HH:MM:SS format
    """
    try:
        # Combine date and time strings
        in_datetime_str = f"{in_date} {in_time}"
        out_datetime_str = f"{out_date} {out_time}"
        
        # Parse to datetime objects
        in_datetime = pd.to_datetime(in_datetime_str)
        out_datetime = pd.to_datetime(out_datetime_str)
        
        # Calculate difference
        worked_duration = out_datetime - in_datetime
        
        # Convert to hours:minutes:seconds format
        total_seconds = int(worked_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
    except Exception:
        return "00:00:00"


def get_default_shift_and_worktype():
    """
    Get default shift and work type for employees without specific assignments.
    
    Returns:
        tuple: (default_shift_name, default_worktype_name)
    """
    try:
        # Try to get a default shift (you might want to customize this logic)
        default_shift = EmployeeShift.objects.first()
        default_shift_name = default_shift.employee_shift if default_shift else "Default Shift"
        
        # Try to get a default work type
        default_worktype = WorkType.objects.first() 
        default_worktype_name = default_worktype.work_type if default_worktype else "Office"
        
        return default_shift_name, default_worktype_name
        
    except Exception:
        return "Default Shift", "Office"


def map_simple_csv_to_system_format(simple_df):
    """
    Transform simple CSV format to system's expected attendance format.
    
    Args:
        simple_df (DataFrame): DataFrame with columns: employee_id, in_date, in_time, out_date, out_time
        
    Returns:
        list: List of dictionaries in system format
    """
    mapped_data = []
    default_shift, default_worktype = get_default_shift_and_worktype()
    
    for index, row in simple_df.iterrows():
        try:
            # Calculate worked hours
            worked_hours = calculate_worked_hours(
                row['in_date'], 
                row['in_time'], 
                row['out_date'], 
                row['out_time']
            )
            
            # Map to system format
            system_row = {
                'Badge ID': str(row['employee_id']).strip(),
                'Shift': default_shift,
                'Work type': default_worktype, 
                'Attendance date': row['in_date'],
                'Check-in date': row['in_date'],
                'Check-in': row['in_time'],
                'Check-out date': row['out_date'],
                'Check-out': row['out_time'],
                'Worked hour': worked_hours,
                'Minimum hour': '08:00:00'  # Default 8 hours minimum
            }
            
            mapped_data.append(system_row)
            
        except Exception as e:
            # Handle mapping errors gracefully
            error_row = {
                'Badge ID': str(row.get('employee_id', 'UNKNOWN')),
                'Shift': default_shift,
                'Work type': default_worktype,
                'Attendance date': row.get('in_date', ''),
                'Check-in date': row.get('in_date', ''),
                'Check-in': row.get('in_time', ''),
                'Check-out date': row.get('out_date', ''),
                'Check-out': row.get('out_time', ''),
                'Worked hour': '00:00:00',
                'Minimum hour': '08:00:00',
                'Mapping Error': f"Row {index + 1}: {str(e)}"
            }
            mapped_data.append(error_row)
    
    return mapped_data


def validate_simple_csv_format(df):
    """
    Validate that the CSV has the required columns and basic data integrity.
    
    Args:
        df (DataFrame): The uploaded CSV DataFrame
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    required_columns = ['employee_id', 'in_date', 'in_time', 'out_date', 'out_time']
    error_messages = []
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        error_messages.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check if DataFrame is empty
    if df.empty:
        error_messages.append("CSV file is empty")
    
    # Basic data validation
    if not error_messages:
        for index, row in df.iterrows():
            row_errors = []
            
            # Check for empty values
            for col in required_columns:
                if pd.isna(row[col]) or str(row[col]).strip() == '':
                    row_errors.append(f"Empty {col}")
            
            if row_errors:
                error_messages.append(f"Row {index + 1}: {', '.join(row_errors)}")
    
    is_valid = len(error_messages) == 0
    return is_valid, error_messages