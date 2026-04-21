from django.contrib import admin
from .models import Meeting
from issues.models import Issue

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('meeting_type', 'date', 'time', 'organizer', 'status')
    list_filter = ('meeting_type', 'status', 'date')
    search_fields = ('location', 'organizer__username', 'agenda_issues__title')
    filter_horizontal = ('attendees', 'agenda_issues')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        class CustomMeetingForm(form):
            def clean(self_form):
                cleaned_data = super().clean()
                role = getattr(request.user, "role", None)
                if not self_form.instance.pk:
                    if role == "HOD":
                        self_form.instance.meeting_type = 'BOS'
                        dept = getattr(request.user, "hod_of", None)
                        self_form.instance.department = dept
                        if dept:
                            self_form.instance.faculty = dept.faculty
                        self_form.instance.organizer = request.user
                    elif role == "DEAN":
                        self_form.instance.meeting_type = 'BOF'
                        self_form.instance.faculty = getattr(request.user, "dean_of", None)
                        self_form.instance.organizer = request.user
                return cleaned_data
        return CustomMeetingForm

    def get_fieldsets(self, request, obj=None):
        if obj is not None:
            # Viewing or editing an existing meeting
            if obj.meeting_type == 'BOF':
                details_fields = ("meeting_type", "faculty", "status")
            else:
                details_fields = ("meeting_type", "department", "faculty", "status")
        else:
            # Creating a new meeting
            role = getattr(request.user, "role", None)
            if not request.user.is_superuser and role in ["HOD", "DEAN"]:
                details_fields = ("status",)
            else:
                details_fields = ("meeting_type", "department", "faculty", "status")

        return (
            ("Meeting Details", {
                "fields": details_fields
            }),
            ("Schedule & Location", {
                "fields": ("date", "time", "location")
            }),
            ("Participants", {
                "fields": ("organizer", "attendees")
            }),
            ("Agenda & Minutes", {
                "fields": ("agenda_issues", "minutes_attachment")
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        role = getattr(request.user, "role", None)
        if role == "TEACHER":
            return [f.name for f in self.model._meta.fields] + ['attendees', 'agenda_issues']
            
        if obj is not None and not request.user.is_superuser:
            # Non-superusers can never edit the core hierarchy rules of a meeting once created
            return ("meeting_type", "department", "faculty", "organizer")
            
        return super().get_readonly_fields(request, obj)

    def save_model(self, request, obj, form, change):
        user = request.user
        role = getattr(user, "role", None)

        # Force assignments for HODs and Deans if they create a new meeting
        if not obj.pk:
            if role == "HOD":
                obj.organizer = user
                obj.meeting_type = Meeting.MeetingType.BOS
                obj.department = getattr(user, "hod_of", None)
            elif role == "DEAN":
                obj.organizer = user
                obj.meeting_type = Meeting.MeetingType.BOF
                obj.faculty = getattr(user, "dean_of", None)
            elif obj.organizer_id is None: # fallback for superusers if left empty
                obj.organizer = user

        super().save_model(request, obj, form, change)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "agenda_issues":
            user = request.user
            role = getattr(user, "role", None)
            # Apply tight filtering for HODs and Deans
            if not user.is_superuser and role != "RECTOR":
                if role == "HOD":
                    if hasattr(user, "hod_of"):
                        # HODs can only add SUBMITTED issues from their department
                        kwargs["queryset"] = Issue.objects.filter(department=user.hod_of, status="SUBMITTED")
                    else:
                        kwargs["queryset"] = Issue.objects.none()
                elif role == "DEAN":
                    if hasattr(user, "dean_of"):
                        # Deans can only add HOD_APPROVED issues from their faculty
                        kwargs["queryset"] = Issue.objects.filter(department__faculty=user.dean_of, status="HOD_APPROVED")
                    else:
                        kwargs["queryset"] = Issue.objects.none()
            else:
                # Optional: Even for superusers we limit what makes sense initially, but let's allow all for now.
                pass
                
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        role = getattr(user, "role", None)

        if user.is_superuser or role == "RECTOR":
            return qs
            
        if role == "DEAN" and hasattr(user, "dean_of"):
            # Deans see all BOF meetings for their faculty, plus BOS meetings within their faculty's departments
            return qs.filter(faculty=user.dean_of) | qs.filter(department__faculty=user.dean_of)
            
        if role == "HOD" and hasattr(user, "hod_of"):
            # HODs exclusively see BOS meetings for their own department
            return qs.filter(department=user.hod_of)
            
        if role == "TEACHER":
            # Teachers only see meetings they are invited to
            return qs.filter(attendees=user)

        return qs.none()

    # Permissions
    def has_module_permission(self, request):
        role = getattr(request.user, "role", None)
        if request.user.is_superuser or role in ["HOD", "DEAN", "RECTOR", "TEACHER"]:
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        role = getattr(request.user, "role", None)
        if request.user.is_superuser or role in ["HOD", "DEAN"]:
            return True
        # Rectors and Teachers don't create meetings
        return False

    def has_change_permission(self, request, obj=None):
        # Only Superusers or the original Organizer can edit the meeting details
        if request.user.is_superuser:
            return True
        if obj is not None and obj.organizer != request.user:
            return False
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Allow HODs and DEANs to delete only their own SCHEDULED meetings to fix mistakes. Superusers can delete anything.
        if request.user.is_superuser:
            return True
        if obj:
            if obj.status == "SCHEDULED" and obj.organizer == request.user:
                return True
            return False
        return False # If obj is None, they don't get the delete button generically unless superuser
