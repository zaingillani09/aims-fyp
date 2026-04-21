from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_router, name='portal_router'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('issues/', views.teacher_issues, name='teacher_issues'),
    path('issues/submit/', views.teacher_submit_issue, name='teacher_submit_issue'),
    path('issues/<int:pk>/', views.teacher_issue_detail, name='teacher_issue_detail'),
    path('meetings/', views.teacher_meetings, name='teacher_meetings'),
    path('meetings/<int:pk>/', views.teacher_meeting_detail, name='teacher_meeting_detail'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
]
