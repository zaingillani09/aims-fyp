from django.urls import path
from .views import first_login_password_change, complete_profile

urlpatterns = [
    path("change-password/", first_login_password_change, name="first_login_password_change"),
    path("complete-profile/", complete_profile, name="complete_profile"),
]