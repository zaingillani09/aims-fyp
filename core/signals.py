from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from issues.models import Issue, IssueDecision
from meetings.models import Meeting
from core.models import Notification
from accounts.models import User

# 1. ISSUE DECISIONS (Legacy hook for direct decision tracking)
@receiver(post_save, sender=IssueDecision)
def notify_issue_decision(sender, instance, created, **kwargs):
    if created:
        issue = instance.issue
        Notification.objects.create(
            recipient=issue.created_by,
            message=f"New decision note added to: '{issue.title}'",
            link=f"/portal/issues/{issue.id}/"
        )

# 2. ISSUE STATUS CHANGES (When agenda status shifts)
@receiver(pre_save, sender=Issue)
def issue_status_notifications(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_issue = Issue.objects.get(pk=instance.pk)
            # Ensure it actually changed, and don't notify the user when THEY just hit "Submit"
            if old_issue.status != instance.status and instance.status != "SUBMITTED":
                Notification.objects.create(
                    recipient=instance.created_by,
                    message=f"Status Update: '{instance.title}' is now {instance.get_status_display()}.",
                    link=f"/portal/issues/{instance.id}/"
                )
        except Issue.DoesNotExist:
            pass

# 3. MEETING M2M (Invitations)
@receiver(m2m_changed, sender=Meeting.attendees.through)
def notify_meeting_attendees(sender, instance, action, pk_set, **kwargs):
    if action == "post_add" and pk_set:
        users = User.objects.filter(pk__in=pk_set)
        for user in users:
            Notification.objects.create(
                recipient=user,
                message=f"You have been invited to a {instance.get_meeting_type_display()}",
                link=f"/portal/meetings/{instance.id}/"
            )

# 4. MEETING UPDATES (Status & Minutes)
@receiver(pre_save, sender=Meeting)
def meeting_update_notifications(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_meeting = Meeting.objects.get(pk=instance.pk)
            status_changed = old_meeting.status != instance.status
            minutes_uploaded = not old_meeting.minutes_attachment and instance.minutes_attachment
            
            if status_changed or minutes_uploaded:
                # Use old_meeting.attendees because pre_save doesn't block existing M2M queries
                for attendee in old_meeting.attendees.all():
                    if status_changed:
                        Notification.objects.create(
                            recipient=attendee,
                            message=f"Meeting Status: {instance.get_meeting_type_display()} is now marked '{instance.get_status_display()}'!",
                            link=f"/portal/meetings/{instance.id}/"
                        )
                    if minutes_uploaded:
                        Notification.objects.create(
                            recipient=attendee,
                            message=f"Minutes were just uploaded for the {instance.get_meeting_type_display()}!",
                            link=f"/portal/meetings/{instance.id}/"
                        )
        except Meeting.DoesNotExist:
            pass
