from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def first_login_password_change(request):
    user = request.user

    # If user already changed password, skip
    if not user.must_change_password:
        return redirect("portal_router")  # temporary redirect for now

    if request.method == "POST":
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            user.must_change_password = False
            user.save()

            return redirect("portal_router")
    else:
        form = PasswordChangeForm(user)

    return render(request, "accounts/first_login_password_change.html", {"form": form})


@login_required
def complete_profile(request):
    user = request.user

    if user.profile_completed:
        return redirect("portal_router")

    if request.method == "POST":
        # Only update the fields the user is allowed to change
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")

        # WE DO NOT TOUCH user.role HERE. 
        # It stays whatever you set it to in the admin panel.

        user.profile_completed = True
        user.save()

        return redirect("portal_router")

    return render(request, "accounts/complete_profile.html")