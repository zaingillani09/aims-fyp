from django.contrib import admin
from .models import Faculty, Department

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "dean")

    def has_module_permission(self, request):
        role = getattr(request.user, "role", None)
        return request.user.is_superuser or role in ["RECTOR", "DEAN"]

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, "role", None) == "RECTOR"

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = getattr(request.user, "role", None)
        if role == "DEAN":
            # the user model defines dean_of or the reverse relationship from one-to-one is dean_of
            return qs.filter(dean=request.user)
        return qs


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "faculty", "hod")
    list_filter = ("faculty",)

    def has_module_permission(self, request):
        role = getattr(request.user, "role", None)
        return request.user.is_superuser or role in ["RECTOR", "DEAN", "HOD"]

    def has_view_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, "role", None) == "RECTOR"

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        role = getattr(request.user, "role", None)
        if role == "DEAN":
            if hasattr(request.user, "dean_of"):
                return qs.filter(faculty=request.user.dean_of)
            return qs.none()
        elif role == "HOD":
            if hasattr(request.user, "hod_of"):
                return qs.filter(id=request.user.hod_of.id)
            return qs.none()
                
        return qs