from django import forms
from django.db import models
from issues.models import Issue
from meetings.models import Meeting

class IssueSubmitForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['title', 'department', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title of the issue...'}),
            'department': forms.Select(),
            'description': forms.Textarea(attrs={'placeholder': 'Detailed description of the issue...', 'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            role = getattr(self.user, 'role', None)
            if role == 'DEAN':
                from core.models import Department
                self.fields['department'].queryset = Department.objects.filter(faculty=self.user.faculty)
            elif role == 'HOD':
                from core.models import Department
                self.fields['department'].queryset = (self.user.departments.all() | Department.objects.filter(hod=self.user)).distinct()
            else:
                self.fields['department'].queryset = self.user.departments.all()

            if self.fields['department'].queryset.count() == 1:
                self.fields['department'].initial = self.fields['department'].queryset.first()

from accounts.models import User

class AttendeeMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username

class MeetingForm(forms.ModelForm):
    attendees = AttendeeMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    class Meta:
        model = Meeting
        fields = ['date', 'time', 'location', 'attendees', 'agenda_issues']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'location': forms.TextInput(attrs={'placeholder': 'Meeting location...'}),
            'agenda_issues': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.meeting_type = kwargs.pop('meeting_type', 'BOS')
        super().__init__(*args, **kwargs)
        
        if self.user:
            from accounts.models import User
            
            # Pre-populate instance fields for model validation
            self.instance.organizer = self.user
            self.instance.meeting_type = self.meeting_type
            
            # Dynamically filter attendees query set based on state to prevent heavy GET load
            if self.is_bound:
                if hasattr(self.data, 'getlist'):
                    selected_ids = self.data.getlist('attendees')
                else:
                    selected_ids = self.data.get('attendees', [])
                    if not isinstance(selected_ids, list):
                        selected_ids = [selected_ids]
                self.fields['attendees'].queryset = User.objects.filter(id__in=selected_ids)
            else:
                if self.instance.pk:
                    self.fields['attendees'].queryset = self.instance.attendees.all()
                else:
                    self.fields['attendees'].queryset = User.objects.none()

            # Filter agenda issues
            if self.meeting_type == 'BOS':
                dept = getattr(self.user, 'hod_of', None)
                if dept:
                    self.instance.department = dept
                    self.fields['agenda_issues'].queryset = Issue.objects.filter(
                        department=dept,
                        status__in=['SUBMITTED', 'RETURNED_TO_HOD']
                    )
            elif self.meeting_type == 'BOF':
                faculty = getattr(self.user, 'dean_of', None)
                if faculty:
                    self.instance.faculty = faculty
                    self.fields['agenda_issues'].queryset = Issue.objects.filter(
                        department__faculty=faculty,
                        status__in=['HOD_APPROVED', 'RETURNED_TO_DEAN']
                    )
            elif self.meeting_type == 'DCM':
                self.fields['agenda_issues'].queryset = Issue.objects.filter(status='DEAN_APPROVED')

    def clean_attendees(self):
        attendees = self.cleaned_data.get('attendees') or []
        from accounts.models import User
        
        if self.meeting_type == 'BOS':
            dept = getattr(self.user, 'hod_of', None)
            if dept:
                for a in attendees:
                    if not dept.members.filter(id=a.id).exists():
                        raise forms.ValidationError(f"{a.get_full_name() or a.username} is not a member of this department.")
        elif self.meeting_type == 'BOF':
            faculty = getattr(self.user, 'dean_of', None)
            if faculty:
                from django.db.models import Q
                for a in attendees:
                    is_faculty_member = a.faculty_id == faculty.id
                    is_hod = a.role == User.Role.HOD
                    if not (is_faculty_member or is_hod):
                        raise forms.ValidationError(f"{a.get_full_name() or a.username} is not authorized for this faculty board.")
        elif self.meeting_type == 'DCM':
            for a in attendees:
                if a.role != User.Role.DEAN:
                    raise forms.ValidationError(f"{a.get_full_name() or a.username} is not a Dean.")
        return attendees

class ConcludeMeetingForm(forms.ModelForm):
    minutes_attachment = forms.FileField(
        required=True,
        error_messages={
            'required': 'You must upload the meeting minutes document to conclude the meeting.'
        },
        widget=forms.FileInput(attrs={'accept': '.pdf,.doc,.docx', 'class': 'form-control'})
    )

    class Meta:
        model = Meeting
        fields = ['minutes_attachment']

    def clean_minutes_attachment(self):
        file = self.cleaned_data.get('minutes_attachment')
        if file:
            name = file.name.lower()
            if not (name.endswith('.pdf') or name.endswith('.doc') or name.endswith('.docx')):
                raise forms.ValidationError("Only .word or .pdf files are accepted here.")
            # Enforce 10MB file size limit
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Minutes document cannot exceed 10 megabytes in size.")
        return file

class IssueDecisionForm(forms.ModelForm):
    class Meta:
        from issues.models import IssueDecision
        model = IssueDecision
        fields = ['decision', 'notes']
        widgets = {
            'decision': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'placeholder': 'Enter your official decision notes here...', 'rows': 4, 'class': 'form-control'}),
        }

