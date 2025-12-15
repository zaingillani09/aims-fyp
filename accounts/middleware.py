from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:

            # Force password change
            if getattr(request.user, "must_change_password", False):
                if request.path != reverse("first_login_password_change"):
                    return redirect("first_login_password_change")

            # Force profile completion
            if getattr(request.user, "profile_completed", False) is False:
                allowed_paths = [
                    reverse("first_login_password_change"),
                    reverse("complete_profile"),
                    "/admin/logout/",
                ]

                if request.path not in allowed_paths:
                    return redirect("complete_profile")

        return self.get_response(request)