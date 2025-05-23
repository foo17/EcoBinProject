
# dashboard/urls.py
from django.urls import path
from . import views
from . import views_analytics
from . import views_reports

app_name = 'analyticsReport'
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('health-check/', views.health_check, name='health_check'),
    path('statistics/', views.statistics, name='statistics'),
    path('universities/', views.universities_list, name='universities_list'),
    path('waste-collection/', views.waste_collection, name='waste_collection'),
    path('campus-experts/', views.campus_experts, name='campus_experts'),
    path('community-breakdown/', views.community_breakdown, name='community_breakdown'),
    path('waste-status/', views.waste_status, name='waste_status'),
    path('recent-collections/', views.recent_collections, name='recent_collections'),
    # analytics_views
    path('component-distribution/', views_analytics.component_distribution, name='component_distribution'),
    path('analytics-highlights/', views_analytics.analytics_highlights, name='analytics_highlights'),
    path('user-role-engagement/', views_analytics.user_role_engagement, name='user_role_engagement'),
    path('waste-insights/', views_analytics.waste_insights, name='waste_insights'),
    path('university-comparison/', views_analytics.university_comparison, name='university_comparison'),
    path('component-processing/', views_analytics.component_processing, name='component_processing'),
    path('component-processing-timeline/', views_analytics.component_processing_timeline, name='component_processing_timeline'),
    # reports_views
    path('reports/', views_reports.reports_view, name='reports'),
    path('report-types/', views_reports.report_types, name='report_types'),
    path('ewaste-collections/', views_reports.ewaste_collections, name='ewaste_collections'),
    path('universities/', views_reports.get_universities, name='get_universities'),
    path('user-activities/', views_reports.user_activities, name='user_activities'),
    path('incentives-report/', views_reports.incentives_report, name='incentives_report'),
    path('component-processing-report/', views_reports.component_processing_report, name='component_processing_report'),
    path('export/', views_reports.export, name='export'),


]