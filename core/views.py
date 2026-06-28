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
    user = request.user
    role = getattr(user, 'role', None)
    
    # 1. Determine base queryset based on role scope
    if role == "TEACHER":
        queryset = Issue.objects.filter(created_by=user)
    elif role == "HOD":
        dept = getattr(user, 'hod_of', None)
        if dept:
            queryset = Issue.objects.filter(department=dept).exclude(status='DRAFT')
        else:
            queryset = Issue.objects.none()
    elif role == "DEAN":
        faculty = getattr(user, 'dean_of', None)
        if faculty:
            queryset = Issue.objects.filter(department__faculty=faculty).exclude(status='DRAFT')
        else:
            queryset = Issue.objects.none()
    elif role == "RECTOR":
        queryset = Issue.objects.exclude(status='DRAFT')
    else:
        queryset = Issue.objects.none()

    # 2. Apply Filters
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q)
        )
        
    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(status=status)
        
    department_id = request.GET.get('department', '').strip()
    if department_id:
        queryset = queryset.filter(department_id=department_id)
        
    creator = request.GET.get('creator', '').strip()
    if creator:
        queryset = queryset.filter(
            Q(created_by__first_name__icontains=creator) |
            Q(created_by__last_name__icontains=creator) |
            Q(created_by__username__icontains=creator)
        )
        
    date_from = request.GET.get('date_from', '').strip()
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
        
    date_to = request.GET.get('date_to', '').strip()
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
        
    issues = queryset.order_by('-created_at')
    
    # Get all active departments for selection lists (for Rector/Dean)
    from core.models import Department
    if role == "RECTOR":
        departments = Department.objects.all().order_by('name')
    elif role == "DEAN" and getattr(user, 'dean_of', None):
        departments = Department.objects.filter(faculty=user.dean_of).order_by('name')
    else:
        departments = []

    # 3. Handle AJAX partial render or full page load
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'
    
    if is_ajax:
        return render(request, 'core/teacher/includes/issues_list_partial.html', {
            'issues': issues,
            'role': role
        })
        
    return render(request, 'core/teacher/issues.html', {
        'issues': issues,
        'departments': departments,
        'role': role,
        'statuses': Issue.Status.choices
    })

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


from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse
import datetime

@login_required
def issue_pdf_report(request, pk):
    from issues.models import Issue
    try:
        issue = Issue.objects.get(pk=pk)
    except Issue.DoesNotExist:
        try:
            issue = Issue.all_objects.get(pk=pk)
        except Issue.DoesNotExist:
            raise Http404("Issue not found")
            
    # Scope permission checks
    user = request.user
    role = getattr(user, 'role', None)
    can_view = False
    
    if role == "TEACHER" and issue.created_by == user:
        can_view = True
    elif role == "HOD" and issue.department == getattr(user, 'hod_of', None):
        can_view = True
    elif role == "DEAN" and issue.department.faculty == getattr(user, 'dean_of', None):
        can_view = True
    elif role == "RECTOR":
        can_view = True
        
    if not can_view:
        raise PermissionDenied("You do not have permission to export this report.")
        
    # Generate the PDF Response
    response = HttpResponse(content_type='application/pdf')
    safe_title = "".join([c if c.isalnum() else "_" for c in issue.title[:30]])
    response['Content-Disposition'] = f'attachment; filename="AIMS_Report_Issue_{issue.id}_{safe_title}.pdf"'
    
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch

    # Setup document
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        name='SubTitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=25
    )
    
    section_heading = ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e1b4b'),
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        name='BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    table_cell_style = ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    
    table_header_style = ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )
    
    story = []
    
    # 1. Header
    story.append(Paragraph("Academic Information Management System (AIMS)", title_style))
    story.append(Paragraph(f"Official Issue Review Log & Action Report — Generated on {datetime.date.today().strftime('%B %d, %Y')}", subtitle_style))
    
    # 2. Metadata Table
    meta_data = [
        [
            Paragraph("<b>Issue ID:</b>", body_style), Paragraph(str(issue.id), body_style),
            Paragraph("<b>Current Status:</b>", body_style), Paragraph(issue.get_status_display(), body_style)
        ],
        [
            Paragraph("<b>Created By:</b>", body_style), Paragraph(issue.created_by.get_full_name() or issue.created_by.username, body_style),
            Paragraph("<b>Date Submitted:</b>", body_style), Paragraph(issue.created_at.strftime("%B %d, %Y at %H:%M") if issue.created_at else "Draft", body_style)
        ],
        [
            Paragraph("<b>Department:</b>", body_style), Paragraph(issue.department.name if issue.department else "N/A", body_style),
            Paragraph("<b>Faculty:</b>", body_style), Paragraph(issue.department.faculty.name if issue.department and issue.department.faculty else "N/A", body_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[1.25*inch, 2.25*inch, 1.25*inch, 2.25*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # 3. Issue Title & Description
    story.append(Paragraph("Issue Description", section_heading))
    story.append(Paragraph(f"<b>Title:</b> {issue.title}", body_style))
    story.append(Spacer(1, 8))
    desc_p = Paragraph(issue.description.replace('\n', '<br/>'), body_style)
    story.append(desc_p)
    story.append(Spacer(1, 15))
    
    # 4. Official Review Notes
    if issue.hod_notes or issue.dean_notes or issue.rector_notes:
        story.append(Paragraph("Official Leadership Decisions", section_heading))
        notes_data = []
        if issue.hod_notes:
            notes_data.append([Paragraph("<b>HOD Notes:</b>", body_style), Paragraph(issue.hod_notes.replace('\n', '<br/>'), body_style)])
        if issue.dean_notes:
            notes_data.append([Paragraph("<b>Dean Notes:</b>", body_style), Paragraph(issue.dean_notes.replace('\n', '<br/>'), body_style)])
        if issue.rector_notes:
            notes_data.append([Paragraph("<b>Rector Notes:</b>", body_style), Paragraph(issue.rector_notes.replace('\n', '<br/>'), body_style)])
            
        notes_table = Table(notes_data, colWidths=[1.5*inch, 5.5*inch])
        notes_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        notes_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(notes_table)
        story.append(Spacer(1, 15))
        
    # 5. Activity History Logs
    history = issue.history.all().order_by('created_at')
    if history.exists():
        story.append(Paragraph("Activity Log & History Timeline", section_heading))
        hist_headers = [
            Paragraph("Date & Time", table_header_style),
            Paragraph("Action", table_header_style),
            Paragraph("Actor", table_header_style),
            Paragraph("Notes / Remarks", table_header_style)
        ]
        
        hist_rows = [hist_headers]
        for item in history:
            time_str = item.created_at.strftime("%b %d, %Y - %H:%M")
            actor_name = f"{item.actor.get_full_name() or item.actor.username} ({item.actor.get_role_display() or item.actor.role})"
            hist_rows.append([
                Paragraph(time_str, table_cell_style),
                Paragraph(item.action, table_cell_style),
                Paragraph(actor_name, table_cell_style),
                Paragraph(item.notes or "No notes added.", table_cell_style)
            ])
            
        hist_table = Table(hist_rows, colWidths=[1.5*inch, 1.5*inch, 2.0*inch, 2.0*inch])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(hist_table)
        
    doc.build(story)
    return response

