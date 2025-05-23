# reports/views.py
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q,  Case, When
from django.db.models.functions import ExtractMonth
from django.core.paginator import Paginator
from django.shortcuts import render
import csv
import json
import pandas as pd
from datetime import date

from ewaste_management.models import (
    University, User, WasteCollectionSlot, Appliance, 
    ActivityRecord, Activity, Incentive, IncentiveRedemptionRecord, 
    Organization, Topic, Comment, Publication, WasteCollectionBooking,
    Component
)
from .utils import get_random_color, validate_report_params


def reports_view(request):
    """Main reports view."""
    return render(request, 'analyticsReport/reports.html')


def report_types(request):
    """Get all report types."""
    report_types = [
        {"value": "ewaste-log", "label": "E-Waste Log"},
        {"value": "user-activity", "label": "User Activity"},
        {"value": "incentives", "label": "Incentives"},
        {"value": "component-processing", "label": "Component Processing"}
    ]
    
    return JsonResponse({"reportTypes": report_types})


def get_universities(request):
    """Get all universities for dropdown."""
    # Get all universities - removed the is_active filter since the field doesn't exist
    universities = University.objects.all().values('id', 'university_name')
    
    university_list = [
        {
            "university_id": uni["id"],
            "university_name": uni["university_name"],
            "is_active": True  # Assuming all universities are active for the frontend
        }
        for uni in universities
    ]
    
    return JsonResponse({"universities": university_list})

@validate_report_params
def ewaste_collections(request):
    """E-Waste Collection Report."""
    university_id = request.GET.get('university_id', 'all')
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    page = int(request.GET.get('page', 1))
    limit = min(max(int(request.GET.get('limit', 10)), 1), 100)
    
    # Base queryset for waste collections - adjusted to WasteCollectionSlot
    # Removed select_related('user') as it doesn't exist in the model
    queryset = WasteCollectionSlot.objects.filter(
        collection_date_time__range=[start_date, end_date]
    ).select_related('organization')
    
    # In the new model, we need to filter by booking->user->university
    if university_id != 'all' and university_id:
        try:
            university_id = int(university_id)
            # Find all bookings for slots where users are from this university
            bookings_from_university = WasteCollectionBooking.objects.filter(
                user__university_id=university_id
            ).values_list('waste_collection_slot_id', flat=True)
            queryset = queryset.filter(id__in=bookings_from_university)
        except ValueError:
            # Handle case where university_id isn't a valid integer
            pass
    
    # Paginator
    paginator = Paginator(queryset.order_by('-collection_date_time'), limit)
    page_obj = paginator.get_page(page)
    
    # Get collections data
    collections = []
    for collection in page_obj:
        # Get bookings for this collection slot
        bookings = WasteCollectionBooking.objects.filter(waste_collection_slot=collection)
        
        # Get first booking's user for university info and booking status
        first_booking = bookings.first()
        university_name = "N/A"
        booking_status = "pending"  # Default status
        
        if first_booking:
            if first_booking.user and first_booking.user.university:
                university_name = first_booking.user.university.university_name
            
            # Get status from the booking, not from the collection slot
            booking_status = first_booking.status
        
        # Get appliances for these bookings
        appliances = Appliance.objects.filter(waste_collection_booking__in=bookings)
        
        # In the new model, we don't have weight field, so count appliances instead
        total_appliances = appliances.count()
        
        # Get list of appliance types in this collection
        appliance_types = appliances.values_list('product_name', flat=True).distinct()
        
        # Get sample serial number (for display purposes)
        serial_number = appliances.exclude(serial_number='').values_list('serial_number', flat=True).first()
        
        collections.append({
            'id': collection.id,
            'collection_date': collection.collection_date_time.isoformat() if collection.collection_date_time else None,
            'university_name': university_name,
            'organization_name': collection.organization.organization_name,
            'waste_type': ', '.join(appliance_types) or 'Mixed E-Waste',
            'weight_kg': total_appliances,  # No weight, using count instead
            'serial_number': serial_number or 'N/A',
            'status': booking_status  # Using status from booking instead of from collection slot
        })
    
    # Get summary data
    total_appliances = 0
    
    # Calculate total number of appliances
    for collection in queryset:
        bookings = WasteCollectionBooking.objects.filter(waste_collection_slot=collection)
        appliance_count = Appliance.objects.filter(waste_collection_booking__in=bookings).count()
        total_appliances += appliance_count
    
    # Calculate processing rates based on booking statuses, not collection slot statuses
    all_bookings = WasteCollectionBooking.objects.filter(
        waste_collection_slot__in=queryset
    )
    total_bookings = all_bookings.count()
    
    processing_count = all_bookings.filter(status__in=['in_progress', 'confirmed']).count()
    completed_count = all_bookings.filter(status__in=['collected']).count()
    
    processing_rate = (processing_count / total_bookings * 100) if total_bookings > 0 else 0
    recycling_rate = (completed_count / total_bookings * 100) if total_bookings > 0 else 0
    
    # Get chart data - using booking status for the chart data as well
    chart_data_queryset = WasteCollectionBooking.objects.filter(
        waste_collection_slot__in=queryset
    )
    
    chart_data = (
        chart_data_queryset
        .annotate(month=ExtractMonth('waste_collection_slot__collection_date_time'))
        .values('month')
        .annotate(
            collected=Count(Case(
                When(status='pending', then=1),
                default=None,
            )),
            processing=Count(Case(
                When(status__in=['confirmed', 'in_progress'], then=1),
                default=None,
            )),
            recycled=Count(Case(
                When(status='collected', then=1),
                default=None,
            ))
        )
        .order_by('month')
    )
    
    # Process chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    formatted_chart_data = {
        'labels': months,
        'collected': [0] * 12,
        'processing': [0] * 12,
        'recycled': [0] * 12
    }
    
    for item in chart_data:
        if item['month'] is not None:
            month_idx = item['month'] - 1
            formatted_chart_data['collected'][month_idx] = item['collected']
            formatted_chart_data['processing'][month_idx] = item['processing']
            formatted_chart_data['recycled'][month_idx] = item['recycled']
    
    return JsonResponse({
        'collections': collections,
        'summary': {
            'total_weight': total_appliances,  # Changed from weight to appliance count
            'total_items': total_appliances,  # For backward compatibility 
            'processing_rate': round(processing_rate),
            'recycling_rate': round(recycling_rate)
        },
        'chartData': formatted_chart_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'items_per_page': limit
        }
    })

@validate_report_params
def user_activities(request):
    """User Activity Report."""
    university_id = request.GET.get('university_id', 'all')
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    page = int(request.GET.get('page', 1))
    limit = min(max(int(request.GET.get('limit', 10)), 1), 100)
    
    # Base queryset for activity records
    queryset = ActivityRecord.objects.filter(
        created_at__range=[start_date, end_date]
    ).select_related('user', 'activity')
    
    if university_id != 'all' and university_id:
        try:
            university_id = int(university_id)
            # Filter users who belong to the specified university - updated for new model
            university_users = User.objects.filter(university_id=university_id)
            queryset = queryset.filter(user__in=university_users)
        except ValueError:
            # Handle case where university_id isn't a valid integer
            pass
    
    # Paginator
    paginator = Paginator(queryset.order_by('-created_at'), limit)
    page_obj = paginator.get_page(page)
    
    # Get activities data
    activities = []
    for activity_record in page_obj:
        # Get university name for the user if they have a university associated
        university_name = "N/A"
        if activity_record.user.university:
            university_name = activity_record.user.university.university_name
        
        activities.append({
            'id': activity_record.id,
            'activity_date': activity_record.created_at.isoformat(),
            'username': activity_record.user.username,
            'university_name': university_name,
            'activity_type': activity_record.activity.activity_type,
            'points_earned': activity_record.point_earned,
            'description': activity_record.activity.description or ''
        })
    
    # Get summary data
    total_activities = queryset.count()
    active_users = queryset.values('user').distinct().count()
    total_points = queryset.aggregate(total=Sum('point_earned'))['total'] or 0
    
    avg_activities_per_user = total_activities / active_users if active_users > 0 else 0
    
    # Get chart data grouped by month and activity type
    chart_data = (
        queryset
        .annotate(month=ExtractMonth('created_at'))
        .values('month', 'activity__activity_type')
        .annotate(count=Count('id'))
        .order_by('month', 'activity__activity_type')
    )
    
    # Process chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Get all unique activity types
    activity_types = list(set(item['activity__activity_type'] for item in chart_data))
    
    # Create datasets with one for each activity type
    datasets = []
    for act_type in activity_types:
        # Create array of 12 zeroes (one for each month)
        data = [0] * 12
        
        # Fill in the data for months that have activities
        for item in chart_data:
            if item['activity__activity_type'] == act_type:
                month_idx = item['month'] - 1  # Convert 1-12 to 0-11
                data[month_idx] = item['count']
        
        # Set color based on activity type
        color = {
            'forum': 'rgba(27, 94, 32, 0.7)',
            'publication': 'rgba(2, 119, 189, 0.7)',
            'recycle': 'rgba(255, 143, 0, 0.7)',
            'other': 'rgba(156, 39, 176, 0.7)'
        }.get(act_type, 'rgba(100, 100, 100, 0.7)')
        
        datasets.append({
            'label': act_type.capitalize(),
            'data': data,
            'backgroundColor': color
        })
    
    return JsonResponse({
        'activities': activities,
        'summary': {
            'total_activities': total_activities,
            'active_users': active_users,
            'total_points': total_points,
            'avg_activities_per_user': round(avg_activities_per_user, 1)
        },
        'chartData': {
            'labels': months,
            'datasets': datasets
        },
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'items_per_page': limit
        }
    })


@validate_report_params
def incentives_report(request):
    """Incentives Report."""
    university_id = request.GET.get('university_id', 'all')
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    page = int(request.GET.get('page', 1))
    limit = min(max(int(request.GET.get('limit', 10)), 1), 100)
    
    # Base queryset for incentive redemption records - updated class name
    queryset = IncentiveRedemptionRecord.objects.filter(
        redemption_date__range=[start_date, end_date]
    ).select_related('user', 'incentive')
    
    if university_id != 'all' and university_id:
        try:
            university_id = int(university_id)
            # Filter users who belong to the specified university - updated for new model
            university_users = User.objects.filter(university_id=university_id)
            queryset = queryset.filter(user__in=university_users)
        except ValueError:
            # Handle case where university_id isn't a valid integer
            pass
    
    # Paginator
    paginator = Paginator(queryset.order_by('-redemption_date'), limit)
    page_obj = paginator.get_page(page)
    
    # Get incentives data
    incentives = []
    for item in page_obj:
        # Get university name for the user if they have a university
        university_name = "N/A"
        if item.user.university:
            university_name = item.user.university.university_name
        
        # In the new model we have 'quantity' instead of 'points_used'
        points_used = item.quantity * item.incentive.points_required
        
        incentives.append({
            'id': item.id,
            'redemption_date': item.redemption_date.isoformat(),
            'username': item.user.username,
            'university_name': university_name,
            'incentive_name': item.incentive.name,
            'points_used': points_used,
            'quantity': item.quantity,
            'status': 'completed'  # No status field in model, assume completed
        })
    
    # Get summary data
    total_redemptions = queryset.count()
    unique_users = queryset.values('user').distinct().count()
    
    # Calculate total points used by multiplying quantity by points_required
    total_points_used = sum(item.quantity * item.incentive.points_required for item in queryset)
    
    # No status field in model, assume all approved/completed (100% approval rate)
    approval_rate = 100
    
    # Get chart data for pie chart
    chart_data = (
        queryset
        .values('incentive__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    
    # Process chart data
    labels = [item['incentive__name'] for item in chart_data]
    data = [item['count'] for item in chart_data]
    background_colors = [get_random_color(0.7) for _ in labels]
    
    return JsonResponse({
        'incentives': incentives,
        'summary': {
            'total_redemptions': total_redemptions,
            'unique_users': unique_users,
            'total_points_used': total_points_used,
            'approval_rate': round(approval_rate)
        },
        'chartData': {
            'labels': labels,
            'data': data,
            'backgroundColor': background_colors
        },
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'items_per_page': limit
        }
    })

@validate_report_params
def component_processing_report(request):
    """Component Processing Report."""
    university_id = request.GET.get('university_id', 'all')
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    page = int(request.GET.get('page', 1))
    limit = min(max(int(request.GET.get('limit', 10)), 1), 100)
    
    # Base queryset for components
    queryset = Component.objects.filter(
        created_at__range=[start_date, end_date]
    ).select_related('appliance')
    
    # Filter by university if specified
    if university_id != 'all' and university_id:
        try:
            university_id = int(university_id)
            # Filter components through appliance and waste_collection_booking
            queryset = queryset.filter(
                appliance__waste_collection_booking__waste_collection_slot__user__university_id=university_id
            )
        except ValueError:
            # Handle case where university_id isn't a valid integer
            pass
    
    # Paginator
    paginator = Paginator(queryset.order_by('-created_at'), limit)
    page_obj = paginator.get_page(page)
    
    # Get component data
    components_data = []
    for component in page_obj:
        # Get appliance and collection data if available
        appliance_name = "N/A"
        serial_number = "N/A"
        collection_date = None
        university_name = "N/A"
        
        if component.appliance:
            appliance_name = component.appliance.product_name
            serial_number = component.appliance.serial_number
            
            try:
                booking = component.appliance.waste_collection_booking
                slot = booking.waste_collection_slot
                collection_date = slot.collection_date_time
                
                if slot.user and slot.user.university:
                    university_name = slot.user.university.university_name
            except:
                pass
        
        components_data.append({
            'id': component.id,
            'component_name': component.component_name,
            'appliance': appliance_name,
            'serial_number': serial_number,
            'collection_date': collection_date.isoformat() if collection_date else None,
            'university': university_name,
            'is_processed': component.is_processed,
            'is_recycled': component.is_recycled,
            'created_at': component.created_at.isoformat(),
        })
    
    # Calculate summary statistics
    total_components = queryset.count()
    processed_count = queryset.filter(is_processed=True).count()
    recycled_count = queryset.filter(is_recycled=True).count()
    
    processing_rate = (processed_count / total_components * 100) if total_components > 0 else 0
    recycling_rate = (recycled_count / total_components * 100) if total_components > 0 else 0
    
    # Get chart data by component type
    chart_data = (
        queryset
        .values('component_name')
        .annotate(
            total=Count('id'),
            processed=Count(Case(When(is_processed=True, then=1))),
            recycled=Count(Case(When(is_recycled=True, then=1)))
        )
        .order_by('-total')
    )
    
    return JsonResponse({
        'components': components_data,
        'summary': {
            'total_components': total_components,
            'processed_components': processed_count,
            'recycled_components': recycled_count,
            'processing_rate': round(processing_rate, 1),
            'recycling_rate': round(recycling_rate, 1)
        },
        'chartData': list(chart_data),
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'items_per_page': limit
        }
    })

def export(request):
    """Export report data in various formats."""
    report_type = request.GET.get("report_type")
    export_format = request.GET.get("format", "csv")
    start_date = request.GET.get('start_date', '2024-01-01')
    end_date = request.GET.get('end_date', date.today().isoformat())
    university_id = request.GET.get('university_id', 'all')

    if not report_type:
        return HttpResponse("Missing report_type", status=400)

    # Fetch data based on report type
    if report_type == "ewaste-log":
        # Get waste collection slots in date range
        collection_slots = WasteCollectionSlot.objects.filter(
            collection_date_time__range=[start_date, end_date]
        )
        
        if university_id != 'all' and university_id:
            try:
                university_id = int(university_id)
                # Find all bookings for slots where users are from this university
                bookings_from_university = WasteCollectionBooking.objects.filter(
                    user__university_id=university_id
                ).values_list('waste_collection_slot_id', flat=True)
                collection_slots = collection_slots.filter(id__in=bookings_from_university)
            except ValueError:
                pass
        
        # Process into export format
        data_list = []
        for slot in collection_slots:
            # Get bookings for this collection slot
            bookings = WasteCollectionBooking.objects.filter(waste_collection_slot=slot)
            
            # Get first booking's user for university info and status
            first_booking = bookings.first()
            university_name = "N/A"
            username = "N/A"
            booking_status = "pending"  # Default status
            
            if first_booking:
                if first_booking.user:
                    username = first_booking.user.username
                    if first_booking.user.university:
                        university_name = first_booking.user.university.university_name
                
                # Get status from booking, not slot
                booking_status = first_booking.status
            
            # Get appliances for these bookings
            appliances = Appliance.objects.filter(waste_collection_booking__in=bookings)
            total_appliances = appliances.count()
            
            # Get types of appliances
            appliance_types = appliances.values_list('product_name', flat=True).distinct()
            waste_type = ', '.join(appliance_types) or 'Mixed E-Waste'
            
            data_list.append({
                "ID": slot.id,
                "Username": username,
                "University": university_name,
                "Organization": slot.organization.organization_name,
                "Waste Type": waste_type,
                "Appliance Count": total_appliances,  # Instead of weight
                "Collection Date": slot.collection_date_time,
                "Status": booking_status  # Using booking status instead of slot status
            })
        
        headers = ["ID", "Username", "University", "Organization", "Waste Type", "Appliance Count", "Collection Date", "Status"]

    elif report_type == "user-activity":
        # Get activity records in date range
        activities = ActivityRecord.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        if university_id != 'all' and university_id:
            try:
                university_id = int(university_id)
                university_users = User.objects.filter(
                    university_id=university_id
                ).values_list('email', flat=True)  # Using email as user's PK
                activities = activities.filter(user_id__in=university_users)
            except ValueError:
                pass
        
        # Process into export format
        data_list = []
        for record in activities:
            # Get university for user
            university_name = "N/A"
            if record.user.university:
                university_name = record.user.university.university_name
                
            data_list.append({
                "ID": record.id,
                "Activity Date": record.created_at,
                "Username": record.user.username,
                "University": university_name,
                "Activity Type": record.activity.activity_type,
                "Points Earned": record.point_earned,
                "Description": record.activity.description or ""
            })
            
        headers = ["ID", "Activity Date", "Username", "University", "Activity Type", "Points Earned", "Description"]

    elif report_type == "incentives":
        # Get incentive records in date range
        incentives = IncentiveRedemptionRecord.objects.filter(
            redemption_date__range=[start_date, end_date]
        )
        
        if university_id != 'all' and university_id:
            try:
                university_id = int(university_id)
                university_users = User.objects.filter(
                    university_id=university_id
                ).values_list('email', flat=True)  # Using email as user's PK
                incentives = incentives.filter(user_id__in=university_users)
            except ValueError:
                pass
            
        # Process into export format
        data_list = []
        for record in incentives:
            # Get university for user
            university_name = "N/A"
            if record.user.university:
                university_name = record.user.university.university_name
            
            # In the new model, points_used is calculated from incentive.points_required * quantity
            points_used = record.quantity * record.incentive.points_required
                
            data_list.append({
                "ID": record.id,
                "Username": record.user.username,
                "University": university_name,
                "Incentive": record.incentive.name,
                "Points Used": points_used,
                "Quantity": record.quantity,
                "Redemption Date": record.redemption_date,
                "Status": "Completed"  # No status field in model, assume completed
            })
            
        headers = ["ID", "Username", "University", "Incentive", "Points Used", "Quantity", "Redemption Date", "Status"]

    elif report_type == "component-processing":
        # Get components in date range
        components = Component.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        if university_id != 'all' and university_id:
            try:
                university_id = int(university_id)
                components = components.filter(
                    appliance__waste_collection_booking__user__university_id=university_id
                )
            except ValueError:
                pass
        
        # Process into export format
        data_list = []
        for component in components:
            # Get appliance details
            appliance_name = "N/A"
            serial_number = "N/A"
            university_name = "N/A"
            collection_date = None
            booking_status = "unknown"  # Default status
            
            if component.appliance:
                appliance_name = component.appliance.product_name
                serial_number = component.appliance.serial_number
                
                try:
                    booking = component.appliance.waste_collection_booking
                    slot = booking.waste_collection_slot
                    collection_date = slot.collection_date_time
                    booking_status = booking.status  # Get status from booking
                    
                    if booking.user and booking.user.university:
                        university_name = booking.user.university.university_name
                except:
                    pass
            
            # Set status values
            process_status = "Processed" if component.is_processed else "Pending"
            recycle_status = "Recycled" if component.is_recycled else ("Pending" if component.is_processed else "Waiting")
            
            data_list.append({
                "ID": component.id,
                "Component": component.component_name,
                "Appliance": appliance_name,
                "Serial Number": serial_number,
                "University": university_name,
                "Collection Date": collection_date,
                "Booking Status": booking_status,  # Added booking status
                "Process Status": process_status,
                "Recycle Status": recycle_status,
                "Created At": component.created_at
            })
            
        headers = ["ID", "Component", "Appliance", "Serial Number", "University", "Collection Date", "Booking Status", "Process Status", "Recycle Status", "Created At"]
    
    else:
        return HttpResponse("Invalid report_type", status=400)

    # Export in selected format
    if export_format == "json":
        response = HttpResponse(json.dumps(data_list, default=str), content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="{report_type}.json"'
        return response

    if export_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{report_type}.csv"'
        writer = csv.writer(response)
        writer.writerow(headers)
        for row in data_list:
            writer.writerow(row.values())
        return response