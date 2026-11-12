
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import StudentRegistrationForm
from .models import AuditLog, UserProfile
from .permissions import get_profile


User = get_user_model()


def record_auth_event(request, event, user=None, identifier=""):
    """Record an authentication event without storing passwords."""

    ip_address = request.META.get("REMOTE_ADDR")

    AuditLog.objects.create(
        user=user,
        event=event,
        identifier=(identifier or (
            user.get_username() if user else ""
        ))[:150],
        ip_address=ip_address,
    )


def register(request):
    if request.method == "POST":
        form = StudentRegistrationForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=data["roll_number"],
                        email=data["email"],
                        password=data["password"],
                    )

                    UserProfile.objects.update_or_create(
                        user=user,
                        defaults={
                            "role": UserProfile.STUDENT,
                            "full_name": data["full_name"],
                            "department": data["department"],
                            "contact_number": data["contact_number"],
                        },
                    )

            except IntegrityError:
                form.add_error(
                    "roll_number",
                    "This roll number is already registered."
                )

            else:
                record_auth_event(
                    request,
                    AuditLog.REGISTRATION,
                    user=user,
                    identifier=data["roll_number"],
                )

                messages.success(
                    request,
                    "Registration successful! You can now log in."
                )
                return redirect("register")

    else:
        form = StudentRegistrationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        identifier = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not identifier or not password:
            record_auth_event(
                request, AuditLog.LOGIN_FAILURE,
                identifier=identifier
            )
            messages.error(request, "Enter both your ID and password.")
            return render(request, "login.html")

        matched_user = User.objects.filter(
            username__iexact=identifier
        ).first()

        profile = get_profile(matched_user) if matched_user else None
        now = timezone.now()

        # Check whether the account is currently locked.
        if profile and profile.locked_until:
            if profile.locked_until > now:
                record_auth_event(
                    request,
                    AuditLog.LOGIN_FAILURE,
                    user=matched_user,
                    identifier=identifier,
                )

                remaining = profile.locked_until - now
                minutes = max(
                    1,
                    int((remaining.total_seconds() + 59) // 60)
                )

                messages.error(
                    request,
                    f"Account temporarily locked. Try again in approximately {minutes} minutes."
                )
                return render(request, "login.html")

            # Lock period has expired.
            profile.failed_login_attempts = 0
            profile.locked_until = None
            profile.save(update_fields=[
                "failed_login_attempts",
                "locked_until",
            ])

        username = (
            matched_user.get_username()
            if matched_user else identifier
        )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            profile = get_profile(user)

            if profile is None:
                record_auth_event(
                    request,
                    AuditLog.LOGIN_FAILURE,
                    user=user,
                    identifier=identifier,
                )

                messages.error(
                    request,
                    "Your account profile is not configured. Contact the administrator."
                )
                return render(request, "login.html")

            # Reset the failed attempts after successful authentication.
            profile.failed_login_attempts = 0
            profile.locked_until = None
            profile.save(update_fields=[
                "failed_login_attempts",
                "locked_until",
            ])

            login(request, user)

            record_auth_event(
                request,
                AuditLog.LOGIN_SUCCESS,
                user=user,
                identifier=identifier,
            )

            messages.success(request, "Login successful!")
            return redirect("home")

        # Incorrect credentials.
        if profile:
            profile.failed_login_attempts += 1

            if profile.failed_login_attempts >= 5:
                profile.locked_until = (
                    timezone.now() + timedelta(minutes=15)
                )

            profile.save(update_fields=[
                "failed_login_attempts",
                "locked_until",
            ])

        record_auth_event(
            request,
            AuditLog.LOGIN_FAILURE,
            user=matched_user,
            identifier=identifier,
        )

        if profile and profile.failed_login_attempts >= 5:
            messages.error(
                request,
                "Five failed attempts! Your account is locked for 15 minutes."
            )
            return render(request, "login.html")

        messages.error(
            request,
            "Invalid ID or password. Please try again."
        )

    return render(request, "login.html")


@login_required
@require_POST
def logout_view(request):
    user = request.user

    record_auth_event(
        request,
        AuditLog.LOGOUT,
        user=user,
        identifier=user.get_username(),
    )

    logout(request)

    messages.success(request, "You have logged out successfully.")
    return redirect("login")
