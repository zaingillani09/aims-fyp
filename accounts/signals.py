from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import User
from core.models import Department

@receiver(m2m_changed, sender=User.departments.through)
def validate_user_departments(sender, instance: User, action, pk_set, **kwargs):
    if action not in ("pre_add", "pre_set"):
        return

    # If you want to allow users without faculty to have departments, remove this block.
    if not instance.faculty_id:
        raise ValidationError("Set user's faculty before assigning departments.")

    bad = Department.objects.filter(pk__in=pk_set).exclude(faculty_id=instance.faculty_id)
    if bad.exists():
        bad_names = ", ".join(bad.values_list("name", flat=True))
        raise ValidationError(f"All departments must be in the user's faculty. Invalid: {bad_names}")