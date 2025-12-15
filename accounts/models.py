from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class User(AbstractUser):

    must_change_password = models.BooleanField(default=True)
    profile_completed = models.BooleanField(default=False)


    class Role(models.TextChoices):
        TEACHER = "TEACHER", "Teacher"
        HOD = "HOD", "HOD"
        DEAN = "DEAN", "Dean"
        RECTOR = "RECTOR", "Rector"
        SYSADMIN = "SYSADMIN", "System Admin"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TEACHER
    )
    primary_department = models.ForeignKey(
        "core.Department",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_users"
    )

    departments = models.ManyToManyField(
        "core.Department",
        blank=True,
        related_name="members"
    )

    faculty = models.ForeignKey(
        "core.Faculty",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="users"
    )

    def clean(self):
        super().clean()

        # Rectors and System Admins do not belong to a faculty or department
        if self.role in [self.Role.RECTOR, self.Role.SYSADMIN]:
            self.faculty = None
            self.primary_department = None


    def save(self, *args, **kwargs):
        if self.role in [self.Role.TEACHER, self.Role.HOD, self.Role.DEAN, self.Role.RECTOR]:
            self.is_staff = True
        self.full_clean()
        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.username