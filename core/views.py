from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from issues.models import Issue
from meetings.models import Meeting
from .forms import IssueSubmitForm, MeetingForm, ConcludeMeetingForm

@login_required
def portal_router(request):
    role = getattr(request.user, 'role', None)
    if role == "HOD":
        return redirect('hod_dashboard')
    elif role == "DEAN":
        return redirect('dean_dashboard')
    elif role == "RECTOR":
        return redirect('rector_dashboard')
    elif request.user.is_superuser:
        return redirect('/admin/')
    return redirect('teacher_dashboard')

@login_required
def teacher_dashboard(request):
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')

    total_issues = Issue.objects.filter(created_by=request.user).count()
    upcoming_meetings = Meeting.objects.filter(attendees=request.user, status='SCHEDULED').count()
    
    context = {
        'total_issues': total_issues,
        'upcoming_meetings': upcoming_meetings,
    }
    return render(request, 'core/teacher/dashboard.html', context)

@login_required
def hod_dashboard(request):
    if getattr(request.user, 'role', None) != "HOD":
        return redirect('portal_router')

    dept = getattr(request.user, 'hod_of', None)
    if not dept:
        messages.warning(request, "You are not assigned as HOD of any department.")
        return render(request, 'core/hod/dashboard.html', {
            'pending_issues_count': 0,
            'upcoming_meetings_count': 0,
            'pending_issues': [],
            'all_issues': [],
            'scheduled_meetings': [],
            'past_meetings': []
        })

    pending_issues = Issue.objects.filter(department=dept, status__in=['SUBMITTED', 'RETURNED_TO_HOD']).order_by('-created_at')
    all_issues = Issue.objects.filter(department=dept).exclude(status='DRAFT').order_by('-updated_at')
    scheduled_meetings = Meeting.objects.filter(department=dept, status='SCHEDULED').order_by('date', 'time')
    past_meetings = Meeting.objects.filter(department=dept, status__in=['CONCLUDED', 'CANCELLED']).order_by('-date', '-time')

    from django.db.models import Count
    status_data = Issue.objects.filter(department=dept).exclude(status='DRAFT').values('status').annotate(count=Count('id'))
    chart_status_labels = [Issue.Status(item['status']).label for item in status_data]
    chart_status_values = [item['count'] for item in status_data]

    context = {
        'department': dept,
        'pending_issues_count': pending_issues.count(),
        'upcoming_meetings_count': scheduled_meetings.count(),
        'pending_issues': pending_issues,
        'all_issues': all_issues,
        'scheduled_meetings': scheduled_meetings,
        'past_meetings': past_meetings,
        'chart_status_labels': chart_status_labels,
        'chart_status_values': chart_status_values,
    }
    return render(request, 'core/hod/dashboard.html', context)

@login_required
def dean_dashboard(request):
    if getattr(request.user, 'role', None) != "DEAN":
        return redirect('portal_router')

    faculty = getattr(request.user, 'dean_of', None)
    if not faculty:
        messages.warning(request, "You are not assigned as Dean of any faculty.")
        return render(request, 'core/dean/dashboard.html', {
            'pending_issues_count': 0,
            'upcoming_meetings_count': 0,
            'pending_issues': [],
            'all_issues': [],
            'scheduled_meetings': [],
            'past_meetings': []
        })

    pending_issues = Issue.objects.filter(department__faculty=faculty, status__in=['HOD_APPROVED', 'RETURNED_TO_DEAN']).order_by('-created_at')
    all_issues = Issue.objects.filter(department__faculty=faculty).exclude(status='DRAFT').order_by('-updated_at')
    scheduled_meetings = Meeting.objects.filter(faculty=faculty, status='SCHEDULED').order_by('date', 'time')
    past_meetings = Meeting.objects.filter(faculty=faculty, status__in=['CONCLUDED', 'CANCELLED']).order_by('-date', '-time')

    from django.db.models import Count
    dept_data = Issue.objects.filter(department__faculty=faculty).exclude(status='DRAFT').values('department__name').annotate(count=Count('id'))
    chart_dept_labels = [item['department__name'] for item in dept_data]
    chart_dept_values = [item['count'] for item in dept_data]

    context = {
        'faculty': faculty,
        'pending_issues_count': pending_issues.count(),
        'upcoming_meetings_count': scheduled_meetings.count(),
        'pending_issues': pending_issues,
        'all_issues': all_issues,
        'scheduled_meetings': scheduled_meetings,
        'past_meetings': past_meetings,
        'chart_dept_labels': chart_dept_labels,
        'chart_dept_values': chart_dept_values,
    }
    return render(request, 'core/dean/dashboard.html', context)

@login_required
def teacher_issues(request):
    role = getattr(request.user, 'role', None)
    if role not in ["TEACHER", "HOD", "DEAN"]:
        return redirect('portal_router')
        
    issues = Issue.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'core/teacher/issues.html', {'issues': issues})

@login_required
def teacher_submit_issue(request):
    role = getattr(request.user, 'role', None)
    if role not in ["TEACHER", "HOD", "DEAN"]:
        return redirect('portal_router')

    if request.method == 'POST':
        form = IssueSubmitForm(request.POST, user=request.user)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            
            if request.POST.get('action') == 'submit':
                try:
                    issue.submit(request.user)
                    if role == "DEAN":
                        messages.success(request, "Your issue has been successfully submitted to the Rector.")
                    elif role == "HOD":
                        messages.success(request, "Your issue has been successfully submitted to your Dean.")
                    else:
                        messages.success(request, "Your issue has been successfully submitted to your HOD.")
                except Exception as e:
                    messages.warning(request, f"Issue saved as draft, but couldn't submit: {str(e)}")
            else:
                messages.success(request, "Your issue has been saved as a Draft.")
                
            return redirect('teacher_issues')
    else:
        form = IssueSubmitForm(user=request.user)

    return render(request, 'core/teacher/submit_issue.html', {'form': form})

@login_required
def teacher_issues_all(request):
    # Fallback/routing view
    return redirect('portal_router')

@login_required
def teacher_meetings(request):
    # Filter meetings that the user attends or organized
    scheduled_meetings = Meeting.objects.filter(
        Q(attendees=request.user) | Q(organizer=request.user),
        status='SCHEDULED'
    ).distinct().order_by('date', 'time')
    past_meetings = Meeting.objects.filter(
        Q(attendees=request.user) | Q(organizer=request.user),
        status__in=['CONCLUDED', 'CANCELLED']
    ).distinct().order_by('-date', '-time')
    return render(request, 'core/teacher/meetings.html', {
        'scheduled_meetings': scheduled_meetings,
        'past_meetings': past_meetings
    })

@login_required
def meeting_create(request):
    role = getattr(request.user, 'role', None)
    if role not in ["HOD", "DEAN", "RECTOR"]:
        return redirect('portal_router')

    if role == 'HOD':
        meeting_type = 'BOS'
    elif role == 'DEAN':
        meeting_type = 'BOF'
    else:
        meeting_type = 'DCM'

    if request.method == 'POST':
        form = MeetingForm(request.POST, user=request.user, meeting_type=meeting_type)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.meeting_type = meeting_type
            
            if role == 'HOD':
                meeting.department = getattr(request.user, 'hod_of', None)
            elif role == 'DEAN':
                meeting.faculty = getattr(request.user, 'dean_of', None)
            # For RECTOR/DCM, meeting.department and meeting.faculty remain None
                
            meeting.save()
            form.save_m2m()
            messages.success(request, f"Successfully scheduled {meeting.get_meeting_type_display()} meeting.")
            if role == 'RECTOR':
                return redirect('rector_dashboard')
            return redirect('teacher_meetings')
    else:
        form = MeetingForm(user=request.user, meeting_type=meeting_type)

    return render(request, 'core/meetings/create_meeting.html', {'form': form, 'meeting_type': meeting_type})

@login_required
def teacher_issue_detail(request, pk):
    role = getattr(request.user, 'role', None)
    if role not in ["TEACHER", "HOD", "DEAN"]:
        return redirect('portal_router')

    issue = get_object_or_404(Issue, pk=pk, created_by=request.user)
    
    editable = False
    if issue.status == 'DRAFT':
        editable = True
    elif issue.status == 'RETURNED' and role == 'TEACHER':
        editable = True
    elif issue.status == 'RETURNED_TO_HOD' and role == 'HOD':
        editable = True
    elif issue.status == 'RETURNED_TO_DEAN' and role == 'DEAN':
        editable = True

    if request.method == 'POST' and editable:
        if request.POST.get('action') == 'delete':
            issue.is_active = False
            issue.save()
            from issues.models import IssueHistory
            IssueHistory.objects.create(
                issue=issue,
                actor=request.user,
                action="Draft Discarded",
                old_status=issue.status,
                new_status=issue.status,
                notes="Draft issue was discarded by creator."
            )
            messages.success(request, "Draft issue has been successfully discarded.")
            return redirect('teacher_issues')

        form = IssueSubmitForm(request.POST, instance=issue, user=request.user)
        if form.is_valid():
            form.save()
            if request.POST.get('action') == 'submit':
                try:
                    issue.submit(request.user)
                    if role == "DEAN":
                        messages.success(request, "Your issue has been successfully submitted to the Rector.")
                    elif role == "HOD":
                        messages.success(request, "Your issue has been successfully submitted to your Dean.")
                    else:
                        messages.success(request, "Your issue has been successfully submitted to your HOD.")
                except Exception as e:
                    messages.warning(request, f"Issue updated safely, but couldn't submit: {str(e)}")
            else:
                from issues.models import IssueHistory
                IssueHistory.objects.create(
                    issue=issue,
                    actor=request.user,
                    action="Draft Updated",
                    old_status=issue.status,
                    new_status=issue.status,
                    notes="Draft issue content edited."
                )
                messages.success(request, "Your draft has been updated successfully.")
            return redirect('teacher_issues')
    else:
        form = IssueSubmitForm(instance=issue, user=request.user)

    history = issue.history.all().order_by('created_at')

    return render(request, 'core/teacher/issue_detail.html', {
        'form': form,
        'issue': issue,
        'editable': editable,
        'history': history,
    })

@login_required
def teacher_meeting_detail(request, pk):
    # Allow view for organizers or attendees
    meeting = get_object_or_404(
        Meeting.objects.filter(
            Q(attendees=request.user) | Q(organizer=request.user)
        ).distinct(),
        pk=pk
    )
    is_organizer = (meeting.organizer == request.user)
    conclude_form = ConcludeMeetingForm() if is_organizer else None

    return render(request, 'core/teacher/meeting_detail.html', {
        'meeting': meeting,
        'is_organizer': is_organizer,
        'conclude_form': conclude_form
    })

@login_required
def meeting_conclude(request, pk):
    role = getattr(request.user, 'role', None)
    if role not in ["HOD", "DEAN", "RECTOR"]:
        return redirect('portal_router')

    meeting = get_object_or_404(Meeting, pk=pk, organizer=request.user)

    if request.method == 'POST':
        form = ConcludeMeetingForm(request.POST, request.FILES, instance=meeting)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.status = Meeting.Status.CONCLUDED
            meeting.save()
            messages.success(request, f"Meeting has been successfully concluded and minutes uploaded.")
            return redirect('teacher_meeting_detail', pk=pk)
        else:
            messages.error(request, "Failed to conclude meeting. Please upload the minutes file.")
            is_organizer = (meeting.organizer == request.user)
            return render(request, 'core/teacher/meeting_detail.html', {
                'meeting': meeting,
                'is_organizer': is_organizer,
                'conclude_form': form
            })
            
    return redirect('teacher_meeting_detail', pk=pk)

@login_required
def meeting_cancel(request, pk):
    role = getattr(request.user, 'role', None)
    if role not in ["HOD", "DEAN", "RECTOR"]:
        return redirect('portal_router')

    meeting = get_object_or_404(Meeting, pk=pk, organizer=request.user)

    if request.method == 'POST':
        meeting.status = Meeting.Status.CANCELLED
        meeting.save()
        messages.success(request, f"Meeting has been successfully cancelled.")
        
    return redirect('teacher_meeting_detail', pk=pk)

@login_required
def mark_notification_read(request, pk):
    from core.models import Notification
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('portal_router')

@login_required
def rector_dashboard(request):
    if getattr(request.user, 'role', None) != "RECTOR":
        return redirect('portal_router')

    pending_issues = Issue.objects.filter(status='DEAN_APPROVED').order_by('-created_at')
    finalized_issues = Issue.objects.filter(status__in=['FINAL_APPROVED', 'REJECTED']).order_by('-updated_at')
    scheduled_meetings = Meeting.objects.filter(
        organizer=request.user,
        status=Meeting.Status.SCHEDULED
    ).order_by('date', 'time')
    past_meetings = Meeting.objects.filter(
        organizer=request.user,
        status__in=[Meeting.Status.CONCLUDED, Meeting.Status.CANCELLED]
    ).order_by('-date', '-time')

    from django.db.models import Count
    # Issues by Faculty
    faculty_data = Issue.objects.exclude(status='DRAFT').values('department__faculty__name').annotate(count=Count('id'))
    chart_faculty_labels = [item['department__faculty__name'] for item in faculty_data]
    chart_faculty_values = [item['count'] for item in faculty_data]
    
    # Issues by Status (Global)
    status_data = Issue.objects.exclude(status='DRAFT').values('status').annotate(count=Count('id'))
    chart_status_labels = [Issue.Status(item['status']).label for item in status_data]
    chart_status_values = [item['count'] for item in status_data]

    context = {
        'pending_issues_count': pending_issues.count(),
        'finalized_issues_count': finalized_issues.count(),
        'pending_issues': pending_issues,
        'finalized_issues': finalized_issues,
        'scheduled_meetings': scheduled_meetings,
        'past_meetings': past_meetings,
        'chart_faculty_labels': chart_faculty_labels,
        'chart_faculty_values': chart_faculty_values,
        'chart_status_labels': chart_status_labels,
        'chart_status_values': chart_status_values,
    }
    return render(request, 'core/rector/dashboard.html', context)

@login_required
def issue_review(request, pk):
    role = getattr(request.user, 'role', None)
    if role not in ["HOD", "DEAN", "RECTOR"]:
        return redirect('portal_router')

    issue = get_object_or_404(Issue, pk=pk)

    # View authorization check (Must belong to department/faculty, and not be a draft)
    view_allowed = False
    if role == "HOD":
        dept = getattr(request.user, 'hod_of', None)
        if dept and issue.department == dept:
            view_allowed = True
    elif role == "DEAN":
        faculty = getattr(request.user, 'dean_of', None)
        if faculty and issue.department.faculty == faculty:
            view_allowed = True
    elif role == "RECTOR":
        # Rector can view any non-draft escalated or decided issue
        view_allowed = (issue.status != 'DRAFT')

    if not view_allowed or issue.status == 'DRAFT':
        messages.error(request, "You do not have permission to view this issue.")
        return redirect('portal_router')

    # Decision authorization check
    can_decide = False
    if role == "HOD" and issue.status in ['SUBMITTED', 'RETURNED_TO_HOD']:
        can_decide = True
    elif role == "DEAN" and issue.status in ['HOD_APPROVED', 'RETURNED_TO_DEAN']:
        can_decide = True
    elif role == "RECTOR" and issue.status == 'DEAN_APPROVED':
        can_decide = True

    from .forms import IssueDecisionForm
    from issues.models import IssueDecision

    form = None
    if can_decide:
        if request.method == 'POST':
            form = IssueDecisionForm(request.POST)
            if form.is_valid():
                decision = form.save(commit=False)
                decision.issue = issue
                decision.decided_by = request.user
                try:
                    # The save method in IssueDecision handles status transition and validation
                    decision.save()
                    messages.success(request, f"Your decision has been successfully recorded for: '{issue.title}'")
                    return redirect('portal_router')
                except Exception as e:
                    messages.error(request, f"Error saving decision: {str(e)}")
        else:
            form = IssueDecisionForm()

    # Get decision history
    decisions = issue.decisions.all().order_by('decided_at')
    history = issue.history.all().order_by('created_at')

    return render(request, 'core/issues/issue_review.html', {
        'issue': issue,
        'form': form,
        'can_decide': can_decide,
        'decisions': decisions,
        'history': history,
    })

@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'core/notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('notifications_list')


from django.http import JsonResponse
from django.db.models import Q

@login_required
def search_attendees(request):
    query = request.GET.get('q', '').strip()
    meeting_type = request.GET.get('meeting_type', 'BOS')
    
    from accounts.models import User
    
    if meeting_type == 'BOS':
        dept = getattr(request.user, 'hod_of', None)
        if dept:
            queryset = dept.members.all()
        else:
            queryset = User.objects.none()
    elif meeting_type == 'BOF':
        faculty = getattr(request.user, 'dean_of', None)
        if faculty:
            queryset = User.objects.filter(
                Q(faculty=faculty) | Q(role=User.Role.HOD)
            ).distinct()
        else:
            queryset = User.objects.none()
    else: # DCM
        queryset = User.objects.filter(role=User.Role.DEAN)
        
    if query:
        queryset = queryset.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) | 
            Q(username__icontains=query)
        )
        
    results = []
    for u in queryset[:20]:
        dept_name = u.primary_department.name if u.primary_department else ""
        role_display = u.get_role_display() if hasattr(u, 'get_role_display') else u.role
        results.append({
            "id": u.id,
            "name": u.get_full_name() or u.username,
            "username": u.username,
            "role": role_display,
            "department": dept_name
        })
    return JsonResponse({"results": results})


@login_required
def meetings_events_api(request):
    from meetings.models import Meeting
    
    meetings = Meeting.objects.filter(
        Q(attendees=request.user) | Q(organizer=request.user)
    ).distinct()
    
    events = []
    for m in meetings:
        if m.status == 'CONCLUDED':
            color = '#10b981' # Green
            text_color = '#ffffff'
        elif m.status == 'CANCELLED':
            color = '#ef4444' # Red
            text_color = '#ffffff'
        else: # SCHEDULED
            color = '#8b5cf6' # Purple
            text_color = '#ffffff'
            
        events.append({
            "id": m.id,
            "title": f"{m.get_meeting_type_display()} Meeting",
            "start": f"{m.date.isoformat()}T{m.time.isoformat()}",
            "url": f"/portal/meetings/{m.id}/",
            "backgroundColor": color,
            "borderColor": color,
            "textColor": text_color,
            "extendedProps": {
                "location": m.location or "TBA",
                "organizer": m.organizer.get_full_name() or m.organizer.username,
                "status": m.get_status_display()
            }
        })
    return JsonResponse(events, safe=False)

