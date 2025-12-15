from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Issue, IssueDecision

# 1. THE INLINE FORM
class IssueDecisionForm(forms.ModelForm):
    class Meta:
        model = IssueDecision
        fields = ("decision", "notes", "decided_by")
        widgets = {'decided_by': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Safety check for readonly states
        if 'decided_by' in self.fields:
            self.fields['decided_by'].required = False

# 2. THE INLINE
class IssueDecisionInline(admin.StackedInline):
    model = IssueDecision
    form = IssueDecisionForm
    extra = 1
    max_num = 5
    can_delete = False

    def get_readonly_fields(self, request, obj=None):
        return ("decided_by", "decided_at")

    def has_add_permission(self, request, obj):
        role = getattr(request.user, "role", None)
        # TEACHER LOCK: Teachers can NEVER add a decision
        if role == "TEACHER":
            return False

        # Role/Status constraints
        if obj:
            if role == "HOD" and obj.status not in ["SUBMITTED", "RETURNED_TO_HOD"]:
                return False
            if role == "DEAN" and obj.status not in ["HOD_APPROVED", "RETURNED_TO_DEAN"]:
                return False
            if role == "RECTOR" and obj.status != "DEAN_APPROVED":
                return False
        return True

    def has_change_permission(self, request, obj=None):
        # Decisions are immutable once created
        return False

# 3. THE MAIN ADMIN CLASS
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "department", "status", "created_at")
    list_filter = ("status", "department")
    search_fields = ("title", "description", "created_by__username")

    def created_by_str(self, obj):
        return obj.created_by.username if obj.created_by else "-"
    created_by_str.short_description = "Created by"

    def department_str(self, obj):
        return str(obj.department) if obj.department else "-"
    department_str.short_description = "Department"

    inlines = [IssueDecisionInline]
    actions = ["submit_issue"]

    def get_fieldsets(self, request, obj=None):
        role = getattr(request.user, "role", None)
        if obj is None or (role == "TEACHER" and obj.status == "RETURNED"):
            user_fields = ("title", "description", "department")
            workflow_fields = ("status",) if obj is None else ("status", "hod_notes", "dean_notes", "rector_notes")
        else:
            if role in ["TEACHER", "HOD", "DEAN", "RECTOR"]:
                user_fields = ("title", "description", "created_by_str", "department_str")
            else:
                user_fields = ("title", "description", "created_by", "department")
            workflow_fields = ("status", "hod_notes", "dean_notes", "rector_notes")
            
        return (
            ("General Information", {"fields": user_fields}),
            ("Workflow Status", {"fields": workflow_fields}),
            ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
        )

    def get_readonly_fields(self, request, obj=None):
        role = getattr(request.user, "role", None)
        readonly = ["status", "hod_notes", "dean_notes", "rector_notes", "created_at", "updated_at"]

        if obj is None:
            return ["status", "created_at", "updated_at"]

        if role == "TEACHER":
            if obj.status == "DRAFT":
                return readonly + ["created_by_str", "department_str"]
            if obj.status == "RETURNED":
                return readonly + ["created_by_str"]
            else:
                return tuple(readonly + ["title", "description", "created_by_str", "department_str"])
        
        if role == "HOD":
            return tuple(readonly + ["title", "description", "created_by_str", "department_str"])
        
        if role == "DEAN":
            return tuple(readonly + ["title", "description", "created_by_str", "department_str"])

        if role == "RECTOR":
            return tuple(readonly + ["title", "description", "created_by_str", "department_str"])
            
        return tuple(readonly)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department" and getattr(request.user, "role", None) == "TEACHER":
            kwargs["queryset"] = request.user.departments.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == IssueDecision:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk:
                    instance.decided_by = request.user
                instance.save()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        role = getattr(user, "role", None)

        # Superusers see everything
        if user.is_superuser: 
            return qs

        # Rectors see only escalated issues ready for their decision or previously finalized
        if role == "RECTOR":
            return qs.filter(status__in=["DEAN_APPROVED", "FINAL_APPROVED", "RETURNED_TO_DEAN"])

        # Deans see issues that the HOD has approved
        if role == "DEAN":
            if hasattr(user, "dean_of"):
                return qs.filter(
                    department__faculty=user.dean_of,
                    status__in=["HOD_APPROVED", "DEAN_APPROVED", "FINAL_APPROVED", "RETURNED_TO_DEAN"]
                )
            return qs.none()

        # HODs see everything in their department EXCEPT drafts
        if role == "HOD":
            if hasattr(user, "hod_of"):
                return qs.filter(department=user.hod_of).exclude(status="DRAFT")
            return qs.none()

        # Teachers see only what they created (including their own drafts)
        if role == "TEACHER":
            return qs.filter(created_by=user)

        return qs.none()

    def has_delete_permission(self, request, obj=None):
        role = getattr(request.user, "role", None)
        if obj:
            if role == "TEACHER":
                # Only delete their own drafts/returned items with no official decision
                has_no_decisions = not obj.decisions.exists()
                return obj.status in ["DRAFT", "RETURNED"] and obj.created_by == request.user and has_no_decisions
            if role == "HOD":
                return False
        return super().has_delete_permission(request, obj)

    def submit_issue(self, request, queryset):
        submitted = 0
        for issue in queryset:
            try:
                issue.submit(by_user=request.user) 
                submitted += 1
            except Exception as e:
                self.message_user(request, f"Error with '{issue.title}': {e}", level='ERROR')
        self.message_user(request, f"Submitted {submitted} issue(s).")
    submit_issue.short_description = "Submit selected issues"

@admin.register(IssueDecision)
class IssueDecisionAdmin(admin.ModelAdmin):
    list_display = ("id", "issue", "decision", "decided_by", "decided_at")
    
    # 1. Prevent non-superusers from seeing the standalone tab
    def has_module_permission(self, request):
        return request.user.is_superuser

    # 1. Prevent HODs from manually creating decisions outside the Issue page
    def has_add_permission(self, request):
        return request.user.is_superuser

    # 2. Prevent HODs from editing a decision once it exists
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    # 3. Prevent HODs from deleting official decisions
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # 4. Make all fields readonly in the detail view
    def get_readonly_fields(self, request, obj=None):
        if obj: # If viewing an existing record
            return [f.name for f in self.model._meta.fields]
        return []