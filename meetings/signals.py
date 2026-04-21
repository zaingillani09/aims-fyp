from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Meeting

@receiver(m2m_changed, sender=Meeting.attendees.through)
def notify_attendees_on_meeting_creation(sender, instance, action, pk_set, **kwargs):
    # Only fire when new attendees are effectively added to the meeting
    if action == "post_add" and pk_set:
        from accounts.models import User
        users_added = User.objects.filter(pk__in=pk_set)
        
        meeting = instance
        subject = f"Meeting Invitation: {meeting.get_meeting_type_display()}"
        message = (
            f"Hello,\n\n"
            f"You have been officially invited to an upcoming {meeting.get_meeting_type_display()} meeting.\n\n"
            f"Details:\n"
            f"Date: {meeting.date}\n"
            f"Time: {meeting.time}\n"
            f"Location: {meeting.location}\n"
            f"Organizer: {meeting.organizer.username}\n\n"
            f"Please ensure you review any attached agenda items prior to the meeting.\n\n"
            f"Regards,\n"
            f"AIMS System Automatically Generated Email"
        )
        
        # Extract emails
        recipient_list = [user.email for user in users_added if user.email]
        
        # If the recipient list has valid emails, utilize Django's send_mail
        if recipient_list:
            send_mail(
                subject,
                message,
                from_email='no-reply@aims.edu',
                recipient_list=recipient_list,
                fail_silently=False,
            )
