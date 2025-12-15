from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError


class Faculty(models.Model):
    name = models.CharField(max_length=150, unique=True)

    dean = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="dean_of",
        limit_choices_to={"role": "DEAN"},
    )

    # ✅ ADD SAVE HERE
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=150)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")

    hod = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="hod_of",
        limit_choices_to={"role": "HOD"},
    )

    def clean(self):
        super().clean()

        if self.hod and getattr(self.hod, "role", None) != "HOD":
            raise ValidationError({"hod": "Assigned HOD must have role=HOD."})

        if self.hod_id and self.pk:
            # HOD must be a member of this department
            if not self.members.filter(pk=self.hod_id).exists():
                raise ValidationError({
                    "hod": "HOD must be a member of this department (in department.members)."
                })

            # HOD's primary_department must be this department
            if self.hod.primary_department_id != self.id:
                raise ValidationError({
                    "hod": "HOD's primary_department must be this department."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        unique_together = ("name", "faculty")

    def __str__(self):
        return f"{self.name} ({self.faculty.name})"