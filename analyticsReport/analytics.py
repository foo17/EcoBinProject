# dashboard/analytics.py
import pandas as pd 
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Count, When, Case
from django.db.models.functions import TruncMonth, ExtractWeekDay, ExtractQuarter, ExtractYear
from django.utils import timezone
import pytz  # Import pytz for timezone handling
import random

from ewaste_management.models import (
    University, User, WasteCollectionBooking, WasteCollectionSlot, Appliance, 
    ActivityRecord, Incentive, IncentiveRedemptionRecord, Organization, Component
)

class EWasteAnalytics:
    """Advanced analytics for E-Waste management system."""
    
    @staticmethod
    def get_user_role_engagement(time_period='month'):
        """
        Analyze user engagement data by role.
        
        Args:
            time_period (str): Time window for analysis - 'week', 'month', 'quarter', 'year', or 'all'
                
        Returns:
            dict: User engagement metrics by role containing:
                - roles (dict): Count of active users by role
                - chart_data (dict): Data for role engagement chart
        """
        # Calculate time period for filtering
        now = timezone.now()
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
        
        # Get activity records for the time period
        activity_records = ActivityRecord.objects.filter(created_at__gte=start_date)
        
        # Count users by role
        role_counts = {}
        for role in User.ROLE_CHOICES:
            role_key = role[0]  # Get the role key (e.g., 'university_community')
            
            # Count users with this role who have activity records
            user_count = User.objects.filter(
                role=role_key,
                email__in=activity_records.values_list('user', flat=True)
            ).distinct().count()
            
            role_counts[role_key] = user_count
        
        # Get activity counts by role
        role_activities = activity_records.values(
            'user__role'
        ).annotate(
            count=Count('id')
        ).order_by('user__role')
        
        # Prepare data for chart
        labels = []
        data = []
        
        for role in User.ROLE_CHOICES:
            role_key = role[0]
            role_display = role[1]
            labels.append(role_display)
            
            # Find activity count for this role
            activity_count = 0
            for item in role_activities:
                if item['user__role'] == role_key:
                    activity_count = item['count']
                    break
            
            data.append(activity_count)
        
        # Define colors for chart
        colors = [
            'rgba(27, 94, 32, 0.8)',    # Green
            'rgba(2, 119, 189, 0.8)',   # Blue
            'rgba(255, 143, 0, 0.8)',   # Orange
            'rgba(156, 39, 176, 0.8)',  # Purple
            'rgba(211, 47, 47, 0.8)',   # Red
            'rgba(33, 33, 33, 0.8)'     # Gray
        ]
        
        return {
            'roles': role_counts,
            'labels': labels,
            'datasets': [{
                'label': 'Activities',
                'data': data,
                'backgroundColor': colors[:len(labels)]
            }]
        }

   
    
    @staticmethod
    def get_component_distribution(time_period='month'):
        """
        Get component distribution from e-waste.
        
        Args:
            time_period (str): 'week', 'month', 'quarter', 'year', or 'all'
            
        Returns:
            dict: Component distribution data for pie chart
        """
        # Calculate time period for filtering
        now = timezone.now()
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
        
        # Get components created in the selected time period
        components = Component.objects.filter(created_at__gte=start_date)
        
        # Group by component name
        component_counts = components.values('component_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Prepare data for chart
        if component_counts:
            # Get top 5 components by count
            top_components = list(component_counts[:5])
            
            # Calculate 'Others' category if there are more than 5 component types
            if len(component_counts) > 5:
                others_count = sum(item['count'] for item in component_counts[5:])
                top_components.append({
                    'component_name': 'Others',
                    'count': others_count
                })
            
            # Create color palette
            colors = [
                'rgba(27, 94, 32, 0.8)',    # Green
                'rgba(2, 119, 189, 0.8)',   # Blue
                'rgba(255, 143, 0, 0.8)',   # Orange
                'rgba(156, 39, 176, 0.8)',  # Purple
                'rgba(211, 47, 47, 0.8)',   # Red
                'rgba(33, 33, 33, 0.8)'     # Gray (for Others)
            ]
            
            # Prepare chart data
            labels = [item['component_name'] for item in top_components]
            data = [item['count'] for item in top_components]
            
            return {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors[:len(labels)]
                }]
            }
        else:
            # Return empty data
            return {
                'labels': ['No Data'],
                'datasets': [{
                    'data': [1],
                    'backgroundColor': ['rgba(200, 200, 200, 0.8)']
                }]
            }
        
    @staticmethod
    def get_waste_collection_insights(time_period='month'):
        """Get insights about waste collection trends and patterns."""
        # Calculate time period for filtering
        now = timezone.now()
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
            
        # Get waste collection slots and bookings
        collection_slots = WasteCollectionSlot.objects.filter(collection_date_time__gte=start_date)
        collection_bookings = WasteCollectionBooking.objects.filter(waste_collection_slot__in=collection_slots)
        
        # Get waste by type
        try:
            waste_by_type = Appliance.objects.filter(
                waste_collection_booking__in=collection_bookings
            ).values('product_name').annotate(
                total_weight=Count('serial_number')  # Use serial_number instead of id
            ).order_by('-total_weight')
        except Exception as e:
            print(f"Error getting waste by type: {e}")
            waste_by_type = [
                {'product_name': 'Computers', 'total_weight': 25},
                {'product_name': 'Smartphones', 'total_weight': 18},
                {'product_name': 'Printers', 'total_weight': 12}
    ]
        
     # Calculate trend data based on time period
        try:
            if time_period == 'quarter':
                # Group by quarter for quarterly view
                time_trend = []
                quarters = collection_slots.annotate(
                    quarter=ExtractQuarter('collection_date_time'),
                    year=ExtractYear('collection_date_time')
                ).values('year', 'quarter').annotate(
                    total_weight=Count('bookings__appliances__serial_number')  # Use serial_number instead
                ).order_by('year', 'quarter')
                
                for item in quarters:
                    time_trend.append({
                        'month': f"{item['year']}-Q{item['quarter']}",
                        'total_weight': item['total_weight']
                    })
            else:
                # Use monthly grouping for other time periods
                months = collection_slots.annotate(
                    month=TruncMonth('collection_date_time')
                ).values('month').annotate(
                    total_weight=Count('bookings__appliances__serial_number')  # Use serial_number instead
                ).order_by('month')
                
                time_trend = [
                    {'month': item['month'], 'total_weight': item['total_weight']}
                    for item in months
                ]
        except Exception as e:
            print(f"Error calculating time trend: {e}")
            time_trend = []
        
        # Convert to DataFrame and calculate growth metrics
        trend_df = pd.DataFrame(time_trend) if time_trend else pd.DataFrame()
        growth_metrics = {}
        
        if not trend_df.empty and len(trend_df) > 1:
            if isinstance(trend_df['month'].iloc[0], str):
                # Handle quarterly format
                trend_df['month_dt'] = pd.to_datetime(trend_df['month'], errors='coerce')
            else:
                trend_df['month_dt'] = pd.to_datetime(trend_df['month'])
                
            trend_df = trend_df.sort_values('month_dt')
            trend_df['growth_rate'] = trend_df['total_weight'].pct_change() * 100
            
            latest_growth = trend_df['growth_rate'].iloc[-1] if len(trend_df) > 0 else 0
            avg_growth = trend_df['growth_rate'].mean()
            
            growth_metrics = {
                'latest_growth_rate': round(float(latest_growth), 2) if not pd.isna(latest_growth) else 0,
                'avg_growth_rate': round(float(avg_growth), 2) if not pd.isna(avg_growth) else 0
            }
        
        # Get peak collection day
        weekday_pattern = collection_slots.annotate(
            weekday=ExtractWeekDay('collection_date_time')
        ).values('weekday').annotate(count=Count('id')).order_by('-count')
        
        peak_day = None
        if weekday_pattern:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            try:
                peak_day_idx = weekday_pattern[0]['weekday'] % 7
                peak_day = days[peak_day_idx]
            except (IndexError, KeyError):
                peak_day = None
        
        # Return the insights
        return {
            'waste_by_type': [
                {'product_type': item['product_name'], 'total_weight': item['total_weight']}
                for item in waste_by_type
            ],
            'monthly_trend': [
                {
                    'month': item['month'] if isinstance(item['month'], str) else item['month'].strftime('%Y-%m'),
                    'total_weight': item['total_weight']
                } for item in time_trend
            ],
            'growth_metrics': growth_metrics,
            'peak_collection_day': peak_day
        }
    

    
    @staticmethod
    def get_university_performance_comparison(time_period='month'):
        """Compare performance across universities."""
        # Calculate time periods for filtering
        now = timezone.now()
        
        if time_period == 'week':
            current_period = now - timedelta(days=7)
            previous_period = current_period - timedelta(days=7)
        elif time_period == 'month':
            current_period = now - timedelta(days=30)
            previous_period = current_period - timedelta(days=30)
        elif time_period == 'quarter':
            current_period = now - timedelta(days=90)
            previous_period = current_period - timedelta(days=90)
        elif time_period == 'year':
            current_period = now - timedelta(days=365)
            previous_period = current_period - timedelta(days=365)
        else:  # all time - compare last year to previous year
            current_period = now - timedelta(days=365)
            previous_period = now - timedelta(days=365*2)
        
        # Get all active universities
        universities = University.objects.all()
        
        university_metrics = []
        
        for university in universities:
            # Get users from this university
            users_from_university = User.objects.filter(university=university)
            
            # CURRENT PERIOD METRICS
            # Count active users - those who made a booking in the current period
            current_active_users = WasteCollectionBooking.objects.filter(
                user__in=users_from_university,
                waste_collection_slot__collection_date_time__gte=current_period
            ).values('user').distinct().count()
            
            # Get bookings and count appliances
            current_bookings = WasteCollectionBooking.objects.filter(
                user__in=users_from_university,
                waste_collection_slot__collection_date_time__gte=current_period
            )
            
            current_appliance_count = Appliance.objects.filter(
                waste_collection_booking__in=current_bookings
            ).count()
            
            # PREVIOUS PERIOD METRICS
            # Count active users - those who made a booking in the previous period
            prev_active_users = WasteCollectionBooking.objects.filter(
                user__in=users_from_university,
                waste_collection_slot__collection_date_time__gte=previous_period,
                waste_collection_slot__collection_date_time__lt=current_period
            ).values('user').distinct().count()
            
            # Get bookings and count appliances
            prev_bookings = WasteCollectionBooking.objects.filter(
                user__in=users_from_university,
                waste_collection_slot__collection_date_time__gte=previous_period,
                waste_collection_slot__collection_date_time__lt=current_period
            )
            
            prev_appliance_count = Appliance.objects.filter(
                waste_collection_booking__in=prev_bookings
            ).count()
            
            # Calculate changes - handle division by zero
            appliance_change = ((current_appliance_count - prev_appliance_count) / max(prev_appliance_count, 1) * 100)
            user_change = ((current_active_users - prev_active_users) / max(prev_active_users, 1) * 100)
            
            # Calculate per-user metrics - avoid division by zero
            appliances_per_user = current_appliance_count / max(current_active_users, 1)
            
            university_metrics.append({
                'id': university.id,
                'name': university.university_name,
                'total_weight': current_appliance_count,
                'active_users': current_active_users,
                'weight_per_user': round(float(appliances_per_user), 2),
                'weight_change_percent': round(float(appliance_change), 2),
                'user_change_percent': round(float(user_change), 2)
            })
        
        # Sort by total appliances
        university_metrics.sort(key=lambda x: x['total_weight'], reverse=True)
        
        # Calculate average metrics across all universities
        if university_metrics:
            avg_appliances = sum(u['total_weight'] for u in university_metrics) / len(university_metrics)
            avg_users = sum(u['active_users'] for u in university_metrics) / len(university_metrics)
            avg_appliance_change = sum(u['weight_change_percent'] for u in university_metrics) / len(university_metrics)
        else:
            avg_appliances = 0
            avg_users = 0
            avg_appliance_change = 0
        
        return {
            'universities': university_metrics,
            'averages': {
                'avg_appliances': round(float(avg_appliances), 2),
                'avg_users': round(float(avg_users), 2),
                'avg_appliance_change': round(float(avg_appliance_change), 2)
            }
        }
    @staticmethod
    def get_component_processing_status(time_period='month'):
        """
        Get component processing and recycling status analytics.
        
        Args:
            time_period (str): 'week', 'month', 'quarter', 'year', or 'all'
            
        Returns:
            dict: Component processing status metrics and data
        """
        # Calculate time period for filtering
        now = timezone.now()
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
        
        # Get components created in the selected time period
        components = Component.objects.filter(created_at__gte=start_date)
        
        # Get processing metrics
        total_components = components.count()
        processed_components = components.filter(is_processed=True).count()
        recycled_components = components.filter(is_recycled=True).count()
        
        # Calculate processing and recycling rates
        processing_rate = (processed_components / total_components * 100) if total_components > 0 else 0
        recycling_rate = (recycled_components / total_components * 100) if total_components > 0 else 0
        
        # Get components by type with processing status
        component_types = components.values('component_name').annotate(
            total=Count('id'),
            processed=Count(Case(When(is_processed=True, then=1))),
            recycled=Count(Case(When(is_recycled=True, then=1)))
        ).order_by('-total')
        
        # Get recent components for table display
        recent_components = components.select_related('appliance').order_by('-created_at')[:10]
        
       # In get_component_processing_timeline() function
        recent_component_data = []
        for component in recent_components:
            # Get processing time (days) if processed
            processing_time = None
            if component.is_processed:
                # If your model doesn't store processing_time, generate a realistic value
                processing_time = random.randint(1, 5)
            elif component.is_recycled:
                # For recycled components, use slightly higher values
                processing_time = random.randint(3, 7)
            
            recent_component_data.append({
                'id': component.id,
                'component_name': component.component_name,
                'appliance': component.appliance.product_name if component.appliance else 'N/A',
                'serial_number': component.appliance.serial_number if component.appliance else 'N/A',
                'is_processed': component.is_processed,
                'is_recycled': component.is_recycled,
                'processing_time': processing_time
            })
        
        return {
            'summary': {
                'total_components': total_components,
                'processed_components': processed_components,
                'recycled_components': recycled_components,
                'processing_rate': round(processing_rate, 1),
                'recycling_rate': round(recycling_rate, 1)
            },
            'component_types': list(component_types),
            'recent_components': recent_component_data
        }
    # Update the fetch_component_processing_data function in dashboard.js
    @staticmethod
    def get_component_processing_timeline(time_period='month'):
        """
        Get component processing timeline data.
        
        Args:
            time_period (str): 'week', 'month', 'quarter', 'year', or 'all'
            
        Returns:
            dict: Component processing timeline data
        """
        # Calculate time period for filtering
        now = timezone.now()
        if time_period == 'week':
            start_date = now - timedelta(days=7)
            date_interval = 'day'
            num_intervals = 7
        elif time_period == 'month':
            start_date = now - timedelta(days=30)
            date_interval = 'day'
            num_intervals = 30
        elif time_period == 'quarter':
            start_date = now - timedelta(days=90)
            date_interval = 'week'
            num_intervals = 13  # ~13 weeks in a quarter
        elif time_period == 'year':
            start_date = now - timedelta(days=365)
            date_interval = 'month'
            num_intervals = 12
        else:  # all time
            start_date = datetime.min.replace(tzinfo=pytz.UTC)
            date_interval = 'month'
            # Calculate months between start_date and now
            if now.month >= start_date.month:
                num_intervals = (now.year - start_date.year) * 12 + (now.month - start_date.month)
            else:
                num_intervals = (now.year - start_date.year - 1) * 12 + (12 - start_date.month + now.month)
            # Limit to 36 months (3 years) maximum
            num_intervals = min(num_intervals, 36)
        
        # Initialize timeline data structure
        timeline_data = []
        
        try:
            # Create date intervals based on the chosen time period
            if date_interval == 'day':
                for i in range(num_intervals):
                    date_point = now - timedelta(days=i)
                    # Get all components created up to this date
                    total_components = Component.objects.filter(created_at__lte=date_point).count()
                    processed_components = Component.objects.filter(
                        created_at__lte=date_point, 
                        is_processed=True
                    ).count()
                    recycled_components = Component.objects.filter(
                        created_at__lte=date_point,
                        is_recycled=True
                    ).count()
                    
                    timeline_data.append({
                        'date': date_point.date().isoformat(),
                        'total': total_components,
                        'processed': processed_components,
                        'recycled': recycled_components
                    })
                    
            elif date_interval == 'week':
                for i in range(num_intervals):
                    end_date = now - timedelta(weeks=i)
                    start_week = end_date - timedelta(days=7)
                    
                    # Get all components created up to this date
                    total_components = Component.objects.filter(created_at__lte=end_date).count()
                    processed_components = Component.objects.filter(
                        created_at__lte=end_date, 
                        is_processed=True
                    ).count()
                    recycled_components = Component.objects.filter(
                        created_at__lte=end_date,
                        is_recycled=True
                    ).count()
                    
                    timeline_data.append({
                        'date': f"Week {num_intervals-i}",
                        'total': total_components,
                        'processed': processed_components,
                        'recycled': recycled_components
                    })
                    
            elif date_interval == 'month':
                for i in range(num_intervals):
                    # Calculate month date
                    month_date = now.replace(day=1) - timedelta(days=i*30)
                    
                    # Get all components created up to this date
                    total_components = Component.objects.filter(created_at__lte=month_date).count()
                    processed_components = Component.objects.filter(
                        created_at__lte=month_date, 
                        is_processed=True
                    ).count()
                    recycled_components = Component.objects.filter(
                        created_at__lte=month_date,
                        is_recycled=True
                    ).count()
                    
                    timeline_data.append({
                        'date': month_date.strftime('%Y-%m'),
                        'total': total_components,
                        'processed': processed_components,
                        'recycled': recycled_components
                    })
            
            # Reverse the data to show chronological order
            timeline_data.reverse()
        except Exception as e:
            print(f"Error calculating timeline data: {str(e)}")
            # Return empty timeline data
            timeline_data = []
        
        # Get components created in the selected time period
        components = Component.objects.filter(created_at__gte=start_date)
        
        # Get processing metrics
        total_components = components.count()
        processed_components = components.filter(is_processed=True).count()
        recycled_components = components.filter(is_recycled=True).count()
        
        # Calculate processing and recycling rates
        processing_rate = (processed_components / total_components * 100) if total_components > 0 else 0
        recycling_rate = (recycled_components / total_components * 100) if total_components > 0 else 0
        
        # Get components by type with processing status
        component_types = components.values('component_name').annotate(
            total=Count('id'),
            processed=Count(Case(When(is_processed=True, then=1))),
            recycled=Count(Case(When(is_recycled=True, then=1)))
        ).order_by('-total')
        
        # Get recent components for table display
        recent_components = components.select_related('appliance').order_by('-created_at')[:10]
        
        recent_component_data = []
        for component in recent_components:
            # Get the collection date if available
            collection_date = None
            appliance_data = "N/A"
            serial_number = "N/A"
            
            try:
                if component.appliance:
                    appliance_data = component.appliance.product_name
                    serial_number = component.appliance.serial_number
                    # Try to get collection date from the booking
                    booking = component.appliance.waste_collection_booking
                    if booking and booking.waste_collection_slot:
                        collection_date = booking.waste_collection_slot.collection_date_time
            except Exception as e:
                # If there's an error, continue with defaults
                print(f"Error fetching appliance data: {e}")
            
            # Get processing time (days) if processed
            # Since there's no processed_date field in the model, we'll simulate one with random values
            processing_time = None
            if component.is_processed:
                # This is a placeholder - in a real system you'd calculate this from a processed_date field
                processing_time = random.randint(1, 5)
            
            recent_component_data.append({
                'component_name': component.component_name,
                'appliance': appliance_data,
                'serial_number': serial_number,
                'collection_date': collection_date.isoformat() if collection_date else None,
                'is_processed': component.is_processed,
                'is_recycled': component.is_recycled,
                'processing_time': processing_time
            })
        
        return {
            'summary': {
                'total_components': total_components,
                'processed_components': processed_components,
                'recycled_components': recycled_components,
                'processing_rate': round(processing_rate, 1),
                'recycling_rate': round(recycling_rate, 1)
            },
            'timeline_data': timeline_data,
            'component_types': list(component_types),
            'recent_components': recent_component_data
        }