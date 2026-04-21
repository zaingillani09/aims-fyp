from django.db import models
from django.conf import settings

class Meeting(models.Model):
    class MeetingType(models.TextChoices):
        BOS = "BOS", "Board of Studies"
        BOF = "BOF", "Board of Faculty"

    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        CONCLUDED = "CONCLUDED", "Concluded"
        CANCELLED = "CANCELLED", "Cancelled"

    meeting_type = models.CharField(max_length=3, choices=MeetingType.choices, default=MeetingType.BOS)
    
    department = models.ForeignKey(
        "core.Department",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="bos_meetings",
        help_text="Required for BOS meetings."
    )
    faculty = models.ForeignKey(
        "core.Faculty",
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="bof_meetings",
        help_text="Required for BOF meetings."
    )
    
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_meetings"
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="attended_meetings",
        blank=True
    )
    
    agenda_issues = models.ManyToManyField(
        "issues.Issue",
        related_name="meetings",
        blank=True
    )
    
    minutes_attachment = models.FileField(upload_to="meeting_minutes/", blank=True, null=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.meeting_type == self.MeetingType.BOS and not self.department:
            raise ValidationError({"department": "Department is required for BOS meetings."})
        if self.meeting_type == self.MeetingType.BOF and not self.faculty:
            raise ValidationError({"faculty": "Faculty is required for BOF meetings."})

    def __str__(self):
        return f"{self.get_meeting_type_display()} on {self.date}"
