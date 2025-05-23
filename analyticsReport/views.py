# dashboard/views.py
from django.http import JsonResponse
from django.db.models import Sum, Count, F, Case, When, Value, FloatField
from django.db.models.functions import ExtractMonth, ExtractQuarter, ExtractYear, TruncMonth
from datetime import datetime, timedelta
import calendar
from ewaste_management.models import (
    University, User, WasteCollectionSlot, WasteCollectionBooking, 
    Appliance, 
    ActivityRecord, Activity, Incentive, IncentiveRedemptionRecord, 
    Organization, Component, Publication
)
from .utils import get_random_color
import random
from django.shortcuts import render
import pytz


def dashboard_view(request):
    """Main dashboard view."""
    return render(request, 'analyticsReport/dashboard.html')


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'OK',
        'message': 'Server is running',
        'timestamp': datetime.now().isoformat()
    })

def statistics(request):
    """Dashboard Statistics."""
    # Calculate basic counts
    university_count = University.objects.count()
    user_count = User.objects.filter(role__in=['university_community', 'campus_expert']).count()
    reward_count = IncentiveRedemptionRecord.objects.count()
    
    # Now calculate total appliances as a proxy for total waste since weight field is gone
    # First get all bookings
    bookings = WasteCollectionBooking.objects.all()
    
    # Count all appliances
    total_appliances = Appliance.objects.filter(waste_collection_booking__in=bookings).count()
    
    return JsonResponse({
        'total_waste': float(total_appliances),  # Using appliance count instead of weight
        'university_count': university_count,
        'user_count': user_count,
        'reward_count': reward_count
    })


def user_list(request):
    """List of users"""
    # Calculate point_earned for each user by summing ActivityRecord points
    users_with_points = []
    for user in User.objects.all():
        total_points = ActivityRecord.objects.filter(user=user).aggregate(
            total_points=Sum('point_earned'))['total_points'] or 0
        
        users_with_points.append({
            'id': user.email,  # Using email as ID since it's the primary key
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'point_earned': total_points
        })
    
    return JsonResponse(users_with_points, safe=False)


def universities_list(request):
    """University List."""
    universities = University.objects.all().order_by('university_name').values('id', 'university_name', 'address')
    return JsonResponse({'universities': list(universities)})

# Update the waste_collection function in views.py
def waste_collection(request):
    """Enhanced E-Waste Collection Trends with device type filtering."""
    year = request.GET.get('year', str(datetime.now().year))
    view_type = request.GET.get('viewType', 'monthly')
    device_type = request.GET.get('deviceType', 'all')
    
    try:
        year_int = int(year)
    except ValueError:
        return JsonResponse({'error': 'Invalid year'}, status=400)
    
    # Use collection_date_time instead of collection_date from WasteCollectionSlot
    slots_by_period = WasteCollectionSlot.objects.filter(
        collection_date_time__year=year_int
    )
    
    # Add device type filtering
    appliances_filter = {}
    if device_type != 'all':
        # Convert device_type to product_name filter
        device_mapping = {
            'computers': ['Computer', 'Laptop', 'Desktop', 'Server'],
            'smartphones': ['Smartphone', 'Mobile Phone', 'Cell Phone'],
            'peripherals': ['Keyboard', 'Mouse', 'USB', 'Adapter', 'Cable'],
            'monitors': ['Monitor', 'Display', 'Screen'],
            'printers': ['Printer', 'Scanner', 'Copier']
        }
        
        if device_type in device_mapping:
            product_names = device_mapping[device_type]
            appliances_filter = {'product_name__in': product_names}
    
    # Build waste data manually with period grouping
    waste_data = []
    
    if view_type == 'monthly':
        # Annotate by month
        slots_by_period = slots_by_period.annotate(
            period=ExtractMonth('collection_date_time')
        )
        labels = list(calendar.month_abbr)[1:]  # ['Jan', 'Feb', ..., 'Dec']
    else:  # quarterly
        # Annotate by quarter
        slots_by_period = slots_by_period.annotate(
            period=ExtractQuarter('collection_date_time')
        )
        labels = ['Q1', 'Q2', 'Q3', 'Q4']
    
    # Get all distinct organization/period combinations
    org_periods = slots_by_period.values('organization__organization_name', 'period').distinct()
    
    for item in org_periods:
        org_name = item['organization__organization_name']
        period = item['period']
        
        # Get slots for this organization in this period
        if view_type == 'monthly':
            slots = WasteCollectionSlot.objects.filter(
                organization__organization_name=org_name,
                collection_date_time__year=year_int,
                collection_date_time__month=period
            )
        else:
            slots = WasteCollectionSlot.objects.filter(
                organization__organization_name=org_name,
                collection_date_time__year=year_int
            ).annotate(
                quarter=ExtractQuarter('collection_date_time')
            ).filter(quarter=period)
        
        # Get bookings for these slots
        bookings = WasteCollectionBooking.objects.filter(
            waste_collection_slot__in=slots
        )
        
        # Apply device type filtering if specified
        appliances_query = Appliance.objects.filter(
            waste_collection_booking__in=bookings
        )
        
        if appliances_filter:
            appliances_query = appliances_query.filter(**appliances_filter)
        
        # Count appliances for these bookings
        appliance_count = appliances_query.count()
        
        waste_data.append({
            'organization__organization_name': org_name,
            'period': period,
            'total_weight': appliance_count  # Using appliance count instead of weight
        })
    
    # Prepare datasets for chart
    organizations = set(item['organization__organization_name'] for item in waste_data)
    
    datasets = []
    for organization in organizations:
        data = [0] * len(labels)
        
        for item in waste_data:
            if item['organization__organization_name'] == organization:
                # Period is 1-based (1-12 for months, 1-4 for quarters)
                data[item['period'] - 1] = float(item['total_weight'])
        
        datasets.append({
            'label': organization,
            'data': data,
            'borderColor': get_random_color(),
            'backgroundColor': get_random_color(0.1),
            'tension': 0.3,
            'fill': True
        })
    
    # Generate additional metadata for enhanced UI
    metadata = {}
    
    # 1. Top device type - Use actual data from the database
    device_counts = Appliance.objects.values('product_name').annotate(
        count=Count('serial_number')
    ).order_by('-count')
    
    if device_counts.exists():
        top_device = device_counts.first()
        total_devices = Appliance.objects.count()
        metadata['top_device'] = {
            'name': top_device['product_name'],
            'percentage': (top_device['count'] / total_devices * 100) if total_devices > 0 else 0
        }
    else:
        metadata['top_device'] = {
            'name': 'No data',
            'percentage': 0
        }
    
    # 2. Collection efficiency (ratio of collected vs target)
    # Calculate from actual data - compare completed collections to total
    total_slots = WasteCollectionSlot.objects.count()
    completed_slots = WasteCollectionSlot.objects.filter(status='completed').count()
    
    if total_slots > 0:
        efficiency = (completed_slots / total_slots) * 100
    else:
        efficiency = 0
    
    metadata['efficiency'] = efficiency
    
    # 3. Monthly growth - Compare current month to previous month
    current_month = datetime.now().month
    prev_month = current_month - 1 if current_month > 1 else 12
    
    current_month_slots = WasteCollectionSlot.objects.filter(
        collection_date_time__year=year_int if current_month > 1 else year_int-1,
        collection_date_time__month=current_month
    )
    prev_month_slots = WasteCollectionSlot.objects.filter(
        collection_date_time__year=year_int if current_month > 1 else year_int-1,
        collection_date_time__month=prev_month
    )
    
    # Get bookings and count appliances
    current_bookings = WasteCollectionBooking.objects.filter(
        waste_collection_slot__in=current_month_slots
    )
    prev_bookings = WasteCollectionBooking.objects.filter(
        waste_collection_slot__in=prev_month_slots
    )
    
    current_count = Appliance.objects.filter(
        waste_collection_booking__in=current_bookings
    ).count()
    prev_count = Appliance.objects.filter(
        waste_collection_booking__in=prev_bookings
    ).count()
    
    # Calculate growth rate
    if prev_count > 0:
        growth_rate = ((current_count - prev_count) / prev_count * 100)
    else:
        growth_rate = 0
    
    metadata['growth'] = growth_rate
    
    # 4. Top collection method
    # Get actual collection methods data from the status field
    collection_methods = WasteCollectionSlot.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    if collection_methods.exists():
        top_method = collection_methods.first()
        total_methods = WasteCollectionSlot.objects.count()
        metadata['top_method'] = {
            'name': top_method['status'].capitalize(),
            'percentage': (top_method['count'] / total_methods * 100) if total_methods > 0 else 0
        }
    else:
        metadata['top_method'] = {
            'name': 'No data',
            'percentage': 0
        }
    
    # Return chart data with metadata
    return JsonResponse({
        'labels': labels,
        'datasets': datasets,
        'metadata': metadata
    })

def campus_experts(request):
    """New API Endpoint for Campus Expert Activities."""
    period = request.GET.get('period', 'month')
    filter_type = request.GET.get('filter', 'all')
    
    # Calculate time period for filtering
    now = datetime.now()
    if period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'quarter':
        start_date = now - timedelta(days=90)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:  # all time
        start_date = datetime(1900, 1, 1)  # Very old date for "all time"
    
    # Get campus experts and their activities
    campus_experts = User.objects.filter(role='campus_expert')
    
    # Get publications data
    publications_query = Publication.objects.filter(
        created_at__gte=start_date
    )
    
    if filter_type == 'publications':
        publications_query = publications_query.filter(user__in=campus_experts)
    
    publications_by_month = publications_query.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Get events data (we'll use Activities with type 'recycle' as a proxy for events)
    events_query = Activity.objects.filter(
        activity_type='recycle',
        created_at__gte=start_date
    )
    
    if filter_type == 'events':
        events_query = ActivityRecord.objects.filter(
            activity__activity_type='recycle',
            created_at__gte=start_date,
            user__in=campus_experts
        ).values('activity').distinct()
        
        events_query = Activity.objects.filter(
            id__in=events_query.values_list('activity', flat=True)
        )
    
    events_by_month = events_query.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Prepare chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    publications_data = [0] * 12
    events_data = [0] * 12
    
    # Fill in publications data
    for pub in publications_by_month:
        month_idx = pub['month'].month - 1  # Convert 1-12 to 0-11
        publications_data[month_idx] = pub['count']
    
    # Fill in events data
    for event in events_by_month:
        month_idx = event['month'].month - 1  # Convert 1-12 to 0-11
        events_data[month_idx] = event['count']
    
    # Get summary metrics
    active_experts = ActivityRecord.objects.filter(
        user__in=campus_experts,
        created_at__gte=start_date
    ).values('user').distinct().count()
    
    total_publications = Publication.objects.filter(
        user__in=campus_experts,
        created_at__gte=start_date
    ).count()
    
    total_events = Activity.objects.filter(
        activity_type='recycle',
        created_at__gte=start_date
    ).count()
    
    # Return chart data with summary
    return JsonResponse({
        'labels': months,
        'datasets': [
            {
                'label': 'Publications',
                'data': publications_data,
                'backgroundColor': 'rgba(2, 119, 189, 0.7)'  # Blue
            },
            {
                'label': 'Events',
                'data': events_data,
                'backgroundColor': 'rgba(255, 143, 0, 0.7)'  # Orange
            }
        ],
        'summary': {
            'active_experts': active_experts,
            'publications': total_publications,
            'events': total_events
        }
    })
def community_breakdown(request):
    """
    API endpoint for community user role distribution.
    Calculates and returns the breakdown of users by role.
    """
    try:
        # Get and validate time period
        time_period = request.GET.get('period', 'month')
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        
        if time_period not in valid_periods:
            return JsonResponse({
                'error': f"Invalid time period. Must be one of {valid_periods}"
            }, status=400)
        
        # Calculate time period for filtering
        now = datetime.now()
        if time_period == 'week':
            start_date = now - timedelta(days=7)
        elif time_period == 'month':
            start_date = now - timedelta(days=30)
        elif time_period == 'quarter':
            start_date = now - timedelta(days=90)
        elif time_period == 'year':
            start_date = now - timedelta(days=365)
        else:  # all time
            start_date = datetime.min.replace(tzinfo=pytz.UTC)
        
        # Get active users in the time period
        active_user_ids = ActivityRecord.objects.filter(
            created_at__gte=start_date
        ).values_list('user', flat=True).distinct()
        
        # Get role distribution of active users
        role_distribution = User.objects.filter(
            pk__in=active_user_ids
        ).values('role').annotate(
            count=Count('pk')
        ).order_by('-count')
        
        # If no data is found, get overall role distribution
        if not role_distribution:
            role_distribution = User.objects.values('role').annotate(
                count=Count('pk')
            ).order_by('-count')
        
        # Prepare data for chart
        if role_distribution:
            # Define friendly names for roles
            role_names = {
                'admin': 'Administrators',
                'university_community': 'University Community',
                'campus_expert': 'Campus Experts',
                'collection_team': 'Collection Team',
                'processing_team': 'Processing Team',
                'recycling_team': 'Recycling Team'
            }
            
            # Create color palette
            colors = [
                'rgba(27, 94, 32, 0.8)',    # Green
                'rgba(2, 119, 189, 0.8)',   # Blue
                'rgba(255, 143, 0, 0.8)',   # Orange
                'rgba(156, 39, 176, 0.8)',  # Purple
                'rgba(211, 47, 47, 0.8)',   # Red
                'rgba(33, 150, 243, 0.8)'   # Light Blue
            ]
            
            # Prepare chart data
            labels = [role_names.get(item['role'], item['role']) for item in role_distribution]
            data = [item['count'] for item in role_distribution]
            
            # Return formatted data for the chart
            return JsonResponse({
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors[:len(labels)]
                }]
            })
        else:
            # Return empty data
            return JsonResponse({
                'labels': ['No Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['rgba(200, 200, 200, 0.8)']
                }]
            })
    
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to fetch community breakdown data',
            'details': str(e)
        }, status=500)
    
def waste_status(request):
    """E-Waste Collection Status."""
    # Get and validate time period
    time_period = request.GET.get('period', 'month')
    valid_periods = ['week', 'month', 'quarter', 'year', 'all']
    
    if time_period not in valid_periods:
        return JsonResponse({
            'error': f"Invalid time period. Must be one of {valid_periods}"
        }, status=400)
    
    # Calculate time period for filtering
    now = datetime.now()
    if time_period == 'week':
        start_date = now - timedelta(days=7)
    elif time_period == 'month':
        start_date = now - timedelta(days=30)
    elif time_period == 'quarter':
        start_date = now - timedelta(days=90)
    elif time_period == 'year':
        start_date = now - timedelta(days=365)
    else:  # all time
        start_date = datetime.min.replace(tzinfo=pytz.UTC)
    
    # Adjust to use WasteCollectionSlot instead of WasteCollection
    # and filter by time period
    status_data = WasteCollectionSlot.objects.filter(
        collection_date_time__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    )
    
    labels = [item['status'] for item in status_data]
    data = [item['count'] for item in status_data]
    
    return JsonResponse({
        'labels': labels,
        'datasets': [{
            'data': data,
            'backgroundColor': [get_random_color() for _ in labels]
        }]
    })



def recent_collections(request):
    """API Endpoint for Recent Waste Collections."""
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    
    try:
        page = int(page)
        limit = int(limit)
    except ValueError:
        return JsonResponse({'error': 'Invalid page or limit'}, status=400)
    
    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get filtered collections - using WasteCollectionSlot
    collection_slots = WasteCollectionSlot.objects.all().order_by('-collection_date_time')
    
    # Get total count for pagination
    total_count = collection_slots.count()
    
    # Apply pagination
    collection_slots = collection_slots[offset:offset + limit]
    
    # Format data for response
    collection_data = []
    for slot in collection_slots:
        # Get bookings for this slot
        bookings = WasteCollectionBooking.objects.filter(waste_collection_slot=slot)
        
        # Get the first booking to find user information and booking status
        first_booking = bookings.first()
        university_name = "N/A"
        booking_status = "pending"  # Default status if no booking is found
        
        # Get university info from the booking's user, not from slot directly
        if first_booking:
            if first_booking.user and first_booking.user.university:
                university_name = first_booking.user.university.university_name
            
            # Use the status from the booking, not from the slot
            booking_status = first_booking.status
        
        # Get appliances for these bookings
        appliances = Appliance.objects.filter(waste_collection_booking__in=bookings)
        
        # Count appliances instead of getting weight
        total_appliances = appliances.count()
        
        # Get product types
        appliance_types = appliances.values_list('product_name', flat=True).distinct()
        
        # Join types with commas if there are multiple
        type_text = ', '.join(appliance_types) if appliance_types else 'Misc. Electronics'
        
        collection_data.append({
            'id': f'WC-{slot.id}',
            'date': slot.collection_date_time.strftime('%Y-%m-%d') if slot.collection_date_time else slot.created_at.strftime('%Y-%m-%d'),
            'university': university_name, 
            'organization': slot.organization.organization_name,
            'type': type_text,
            'weight': f'{total_appliances}',  # Using appliance count as a proxy for weight
            'status': booking_status  # Using status from the booking instead of the slot
        })
    
    return JsonResponse({
        'collections': collection_data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'total_pages': (total_count + limit - 1) // limit  # Ceiling division
        }
    })