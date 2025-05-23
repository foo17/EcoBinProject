# dashboard/utils.py
import random
from datetime import datetime
from functools import wraps
from django.http import JsonResponse

def get_random_color(alpha=1.0):
    """Generate a random color with optional alpha value."""
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgba({r}, {g}, {b}, {alpha})"

def format_date(date_obj):
    """Format date to YYYY-MM-DD."""
    if not isinstance(date_obj, datetime):
        try:
            date_obj = datetime.strptime(str(date_obj), '%Y-%m-%d')
        except (ValueError, TypeError):
            return None
    
    return date_obj.strftime('%Y-%m-%d')

def format_number(num):
    """Format number with commas for thousands separators."""
    return "{:,}".format(num)

def calculate_percentage(part, total):
    """Calculate percentage safely."""
    if not total:
        return 0
    return round((part / total) * 100)


# Report utils
def validate_date(date_str, default_value):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
    except ValueError:
        return default_value
    
    
def is_valid_date(date_string):
    """Validate date string (YYYY-MM-DD)."""
    if not date_string or not isinstance(date_string, str):
        return False
    
    if not date_string.strip():
        return False
    
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def is_valid_id(id_string):
    """Validate numeric ID."""
    try:
        num_id = int(id_string)
        return num_id > 0
    except (ValueError, TypeError):
        return False

def is_valid_year(year_string):
    """Validate year."""
    try:
        num_year = int(year_string)
        current_year = datetime.now().year
        return 2000 <= num_year <= current_year + 1
    except (ValueError, TypeError):
        return False

def validate_report_params(view_func):
    """Decorator for validating report parameters."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        university_id = request.GET.get('university_id')
        page = request.GET.get('page')
        limit = request.GET.get('limit')
        
        errors = []
        
        if start_date and not is_valid_date(start_date):
            errors.append('Invalid start date format. Use YYYY-MM-DD')
        
        if end_date and not is_valid_date(end_date):
            errors.append('Invalid end date format. Use YYYY-MM-DD')
        
        if university_id and university_id != 'all' and not is_valid_id(university_id):
            errors.append('Invalid university ID')
        
        if page and not page.isdigit():
            errors.append('Page must be a number')
        
        if limit and not limit.isdigit():
            errors.append('Limit must be a number')
        
        if errors:
            return JsonResponse({'errors': errors}, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
