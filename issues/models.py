from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Issue(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted to HOD"
        HOD_APPROVED = "HOD_APPROVED", "HOD Approved (Pending Faculty Board)"
        DEAN_APPROVED = "DEAN_APPROVED", "Dean Approved (Pending Deans Committee)"
        FINAL_APPROVED = "FINAL_APPROVED", "Final Approval (Rector)"
        REJECTED = "REJECTED", "Rejected"
        RETURNED = "RETURNED", "Returned for Revision"
        RETURNED_TO_HOD = "RETURNED_TO_HOD", "Returned to HOD for Revision"
        RETURNED_TO_DEAN = "RETURNED_TO_DEAN", "Returned to Dean for Revision"

    title = models.CharField(max_length=200)
    description = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issues_created"
    )

    department = models.ForeignKey(
        "core.Department",
        on_delete=models.PROTECT,
        related_name="issues"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )

    hod_notes = models.TextField(blank=True, help_text="Final decision notes from the process")
    dean_notes = models.TextField(blank=True, help_text="Dean decision notes from the process")
    rector_notes = models.TextField(blank=True, help_text="Rector decision notes from the process")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.created_by_id and self.department_id:
            role = getattr(self.created_by, 'role', None)
            if role == "DEAN":
                if self.department.faculty_id != self.created_by.faculty_id:
                    raise ValidationError({
                        "department": "As a Dean, you can only submit an issue to a department within your faculty."
                    })
            elif role == "HOD":
                hod_dept = getattr(self.created_by, 'hod_of', None)
                if hod_dept != self.department and not self.created_by.departments.filter(pk=self.department_id).exists():
                    raise ValidationError({
                        "department": "As an HOD, you can only submit an issue to a department you represent or belong to."
                    })
            else:
                if not self.created_by.departments.filter(pk=self.department_id).exists():
                    raise ValidationError({
                        "department": "You can only submit an issue to a department you belong to."
                    })

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        is_raw = kwargs.get('raw', False)
        # Only run full_clean if we are not in a 'raw' state (like migrations)
        if not is_raw:
            self.full_clean()
        result = super().save(*args, **kwargs)
        if is_new and not is_raw:
            IssueHistory.objects.create(
                issue=self,
                actor=self.created_by,
                action="Created Draft",
                new_status=self.status,
                notes="Issue drafted."
            )
        return result

    def submit(self, by_user):
        if by_user.id != self.created_by_id:
            raise ValidationError("Only the creator can submit this issue.")

        # Determine which statuses are allowed for submission based on role
        allowed_statuses = [self.Status.DRAFT, self.Status.RETURNED]
        if by_user.role == "HOD":
            allowed_statuses.append(self.Status.RETURNED_TO_HOD)
        elif by_user.role == "DEAN":
            allowed_statuses.append(self.Status.RETURNED_TO_DEAN)

        if self.status not in allowed_statuses:
            raise ValidationError("This issue is not in a submittable state.")

        old_status = self.status

        # Determine next status based on who is submitting
        if by_user.role == "DEAN":
            # Dean submits directly to Rector (pending Rector review)
            self.status = self.Status.DEAN_APPROVED
            target_role = "Rector"
        elif by_user.role == "HOD":
            # HOD submits directly to Dean (pending Faculty Board review)
            self.status = self.Status.HOD_APPROVED
            target_role = "Dean"
        else:
            # Teacher submits to HOD
            if not self.department.hod_id:
                raise ValidationError("Cannot submit: this department has no HOD assigned.")
            self.status = self.Status.SUBMITTED
            target_role = "HOD"
        
        self.save()

        # Log submission history
        role_label = by_user.get_role_display() if hasattr(by_user, 'get_role_display') else by_user.role
        IssueHistory.objects.create(
            issue=self,
            actor=by_user,
            action=f"Submitted to {target_role}",
            old_status=old_status,
            new_status=self.status,
            notes=f"Issue submitted for review by {role_label}."
        )

    def __str__(self):
        return f"{self.title} [{self.get_status_display()}]"


class IssueDecision(models.Model):
    class Decision(models.TextChoices):
        APPROVE = "APPROVE", "Approve"
        REJECT = "REJECT", "Reject"
        RETURN = "RETURN", "Return for Revision"

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="decisions"
    )

    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="issue_decisions"
    )

    decision = models.CharField(max_length=10, choices=Decision.choices)
    notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        
        if not hasattr(self, 'decided_by') or not self.decided_by_id:
            return  # Allow admin bypass during pre-save
            
        role = self.decided_by.role
        
        if role == "HOD":
            hod = self.issue.department.hod
            if not hod:
                raise ValidationError({"issue": "This issue's department has no HOD assigned yet."})
            if self.decided_by_id != hod.id:
                raise ValidationError({"decided_by": "Only the HOD of this department can make the initial decision."})
            if self.issue.status not in [Issue.Status.SUBMITTED, Issue.Status.RETURNED_TO_HOD]:
                raise ValidationError({"issue": "HOD can only decide on issues that are currently SUBMITTED or RETURNED_TO_HOD."})
                
        elif role == "DEAN":
            if not hasattr(self.decided_by, 'dean_of') or self.decided_by.dean_of != self.issue.department.faculty:
                raise ValidationError({"decided_by": "You are not the assigned Dean of this faculty."})
            if self.issue.status not in [Issue.Status.HOD_APPROVED, Issue.Status.RETURNED_TO_DEAN]:
                raise ValidationError({"issue": "Dean can only decide on issues that are currently HOD_APPROVED or RETURNED_TO_DEAN."})
                
        elif role == "RECTOR":
            if self.issue.status != Issue.Status.DEAN_APPROVED:
                raise ValidationError({"issue": "Rector can only decide on issues that are currently DEAN_APPROVED."})
                
        elif self.decided_by.is_superuser:
            pass # Superuser/Rector can bypass
        else:
            raise ValidationError({"decided_by": "You do not have permission to make a decision on this issue."})

    def save(self, *args, **kwargs):
        self.full_clean()
        
        old_status = self.issue.status
        # Save the decision record
        result = super().save(*args, **kwargs)

        role = self.decided_by.role if hasattr(self, 'decided_by') and self.decided_by else None

        if role == "HOD" or (role not in ["HOD", "DEAN", "RECTOR"] and self.issue.status in [Issue.Status.SUBMITTED, Issue.Status.RETURNED_TO_HOD]):
            if self.decision == self.Decision.APPROVE:
                self.issue.status = Issue.Status.HOD_APPROVED
            elif self.decision == self.Decision.REJECT:
                self.issue.status = Issue.Status.REJECTED
            elif self.decision == self.Decision.RETURN:
                self.issue.status = Issue.Status.RETURNED
            
            self.issue.hod_notes = self.notes
            self.issue.save(update_fields=['status', 'hod_notes'])
            
        elif role == "DEAN" or (role not in ["HOD", "DEAN", "RECTOR"] and self.issue.status in [Issue.Status.HOD_APPROVED, Issue.Status.RETURNED_TO_DEAN]):
            if self.decision == self.Decision.APPROVE:
                self.issue.status = Issue.Status.DEAN_APPROVED
            elif self.decision == self.Decision.REJECT:
                self.issue.status = Issue.Status.REJECTED
            elif self.decision == self.Decision.RETURN:
                self.issue.status = Issue.Status.RETURNED_TO_HOD
            
            self.issue.dean_notes = self.notes
            self.issue.save(update_fields=['status', 'dean_notes'])

        elif role == "RECTOR" or (role not in ["HOD", "DEAN", "RECTOR"] and self.issue.status == Issue.Status.DEAN_APPROVED):
            if self.decision == self.Decision.APPROVE:
                self.issue.status = Issue.Status.FINAL_APPROVED
            elif self.decision == self.Decision.REJECT:
                self.issue.status = Issue.Status.REJECTED
            elif self.decision == self.Decision.RETURN:
                self.issue.status = Issue.Status.RETURNED_TO_DEAN
            
            self.issue.rector_notes = self.notes
            self.issue.save(update_fields=['status', 'rector_notes'])

        # Log decision history
        decision_label = self.get_decision_display()
        action_name = f"{role} Decision: {decision_label}"
        IssueHistory.objects.create(
            issue=self.issue,
            actor=self.decided_by,
            action=action_name,
            old_status=old_status,
            new_status=self.issue.status,
            notes=self.notes
        )

        return result

    def __str__(self):
        role = self.decided_by.role if hasattr(self, 'decided_by') and self.decided_by else "Unknown"
        return f"{role} Decision: {self.issue.title} - {self.decision}"


class IssueHistory(models.Model):
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="history"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issue_history_actions"
    )
    action = models.CharField(max_length=100)
    old_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.issue.title} - {self.action} by {self.actor.username if self.actor else 'System'} at {self.created_at}"