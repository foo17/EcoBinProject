# analytics/views.py
import logging
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET
from .analytics import EWasteAnalytics
from django.shortcuts import render
from ewaste_management.models import WasteCollectionSlot

# Configure logging
logger = logging.getLogger(__name__)

def analytics_view(request):
    return render(request, 'analytics.html')

@require_GET
def user_role_engagement(request):
    """API endpoint for user engagement by role."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get user role engagement data from analytics class
        data = EWasteAnalytics.get_user_role_engagement(time_period)
        logger.info(f"User role engagement metrics fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching user role engagement metrics: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch user role engagement metrics',
            'details': str(e)
        }, status=500)
    

@require_GET
def component_distribution(request):
    """API endpoint for component distribution from e-waste."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get component distribution data from analytics class
        data = EWasteAnalytics.get_component_distribution(time_period)
        logger.info(f"Component distribution data fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching component distribution data: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch component distribution data',
            'details': str(e)
        }, status=500)
    


@require_GET
def waste_insights(request):
    """API endpoint for waste collection insights."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get waste insights data
        data = EWasteAnalytics.get_waste_collection_insights(time_period)
        logger.info(f"Waste collection insights fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching waste collection insights: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch waste collection insights',
            'details': str(e)
        }, status=500)



@require_GET
def university_comparison(request):
    """API endpoint for university performance comparison."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get university comparison data
        data = EWasteAnalytics.get_university_performance_comparison(time_period)
        logger.info(f"University performance comparison fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching university performance comparison: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch university performance comparison',
            'details': str(e)
        }, status=500)



@require_GET
def analytics_highlights(request):
    """API endpoint for dashboard analytics highlights."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get waste insights for growth metrics and peak day
        waste_insights = EWasteAnalytics.get_waste_collection_insights(time_period)
        
        # Get all waste collection slots (fixed from WasteCollection to WasteCollectionSlot)
        queryset = WasteCollectionSlot.objects.all()
        
        # Calculate processing rates exactly as in ewaste_collections
        processing_count = queryset.filter(status__in=['in_progress', 'completed']).count()
        total_count = queryset.count()
        
        # Calculate processing rate
        processing_rate = (processing_count / total_count * 100) if total_count > 0 else 0
        
        # Prepare response data
        highlights = {
            'forecasted_growth': waste_insights.get('growth_metrics', {}).get('avg_growth_rate', 0),
            'processing_rate': round(processing_rate),
            'peak_collection_day': waste_insights.get('peak_collection_day', 'Monday')
        }
        
        logger.info(f"Analytics highlights fetched for period: {time_period}")
        
        return JsonResponse(highlights)
    
    except Exception as e:
        logger.error(f"Error fetching analytics highlights: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch analytics highlights',
            'details': str(e)
        }, status=500)


@require_GET
def component_processing(request):
    """API endpoint for component processing and recycling status."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get component processing data from analytics class
        data = EWasteAnalytics.get_component_processing_status(time_period)
        logger.info(f"Component processing data fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching component processing data: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch component processing data',
            'details': str(e)
        }, status=500)
    

@require_GET
def component_processing_timeline(request):
    """API endpoint for component processing timeline data."""
    try:
        time_period = request.GET.get('period', 'month')
        
        # Validate time period
        valid_periods = ['week', 'month', 'quarter', 'year', 'all']
        if time_period not in valid_periods:
            logger.warning(f"Invalid time period received: {time_period}")
            return HttpResponseBadRequest(f"Invalid time period. Must be one of {valid_periods}")
        
        # Get component processing data with timeline data
        data = EWasteAnalytics.get_component_processing_timeline(time_period)
        logger.info(f"Component processing timeline data fetched for period: {time_period}")
        
        return JsonResponse(data)
    
    except Exception as e:
        logger.error(f"Error fetching component processing timeline data: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Failed to fetch component processing timeline data',
            'details': str(e)
        }, status=500)

