from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from issues.models import Issue
from meetings.models import Meeting
from .forms import IssueSubmitForm
from django.contrib import messages

@login_required
def portal_router(request):
    role = getattr(request.user, 'role', None)
    if request.user.is_superuser or role in ["HOD", "DEAN", "RECTOR"]:
        return redirect('/admin/')
    return redirect('teacher_dashboard')

@login_required
def teacher_dashboard(request):
    # Restrict to teachers
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
def teacher_issues(request):
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')
        
    issues = Issue.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'core/teacher/issues.html', {'issues': issues})

@login_required
def teacher_submit_issue(request):
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')

    if request.method == 'POST':
        form = IssueSubmitForm(request.POST, user=request.user)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.created_by = request.user
            issue.save()
            
            # If the user clicked "Submit to HOD", transition the state
            if request.POST.get('action') == 'submit':
                try:
                    issue.submit(request.user)
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
def teacher_meetings(request):
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')

    meetings = Meeting.objects.filter(attendees=request.user).order_by('date', 'time')
    return render(request, 'core/teacher/meetings.html', {'meetings': meetings})

@login_required
def teacher_issue_detail(request, pk):
    from django.shortcuts import get_object_or_404
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')

    issue = get_object_or_404(Issue, pk=pk, created_by=request.user)
    editable = issue.status in ['DRAFT', 'RETURNED']

    if request.method == 'POST' and editable:
        form = IssueSubmitForm(request.POST, instance=issue, user=request.user)
        if form.is_valid():
            form.save()
            if request.POST.get('action') == 'submit':
                try:
                    issue.submit(request.user)
                    messages.success(request, "Your issue has been successfully submitted to your HOD.")
                except Exception as e:
                    messages.warning(request, f"Issue updated safely, but couldn't submit: {str(e)}")
            else:
                messages.success(request, "Your draft has been updated successfully.")
            return redirect('teacher_issues')
    else:
        form = IssueSubmitForm(instance=issue, user=request.user)

    return render(request, 'core/teacher/issue_detail.html', {
        'form': form,
        'issue': issue,
        'editable': editable
    })

@login_required
def teacher_meeting_detail(request, pk):
    from django.shortcuts import get_object_or_404
    if getattr(request.user, 'role', None) != "TEACHER":
        return redirect('portal_router')

    meeting = get_object_or_404(Meeting, pk=pk, attendees=request.user)
    return render(request, 'core/teacher/meeting_detail.html', {'meeting': meeting})

@login_required
def mark_notification_read(request, pk):
    from django.shortcuts import get_object_or_404
    from core.models import Notification
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('teacher_dashboard')
