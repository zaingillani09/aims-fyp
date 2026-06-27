from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_router, name='portal_router'),
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('dean/dashboard/', views.dean_dashboard, name='dean_dashboard'),
    path('rector/dashboard/', views.rector_dashboard, name='rector_dashboard'),
    path('issues/', views.teacher_issues, name='teacher_issues'),
    path('issues/submit/', views.teacher_submit_issue, name='teacher_submit_issue'),
    path('issues/<int:pk>/', views.teacher_issue_detail, name='teacher_issue_detail'),
    path('issues/<int:pk>/review/', views.issue_review, name='issue_review'),
    path('meetings/', views.teacher_meetings, name='teacher_meetings'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:pk>/', views.teacher_meeting_detail, name='teacher_meeting_detail'),
    path('meetings/<int:pk>/conclude/', views.meeting_conclude, name='meeting_conclude'),
    path('meetings/<int:pk>/cancel/', views.meeting_cancel, name='meeting_cancel'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('meetings/search-attendees/', views.search_attendees, name='search_attendees'),
    path('meetings/events/', views.meetings_events_api, name='meetings_events_api'),
]
