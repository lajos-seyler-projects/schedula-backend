from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from django.conf import settings
from django.core.mail import send_mail


def get_registration_email_html(user):
    activation_link = user.get_activation_link()
    project_name = settings.PROJECT_NAME

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2>Welcome to {project_name}!</h2>
        
        <p>Hi {user.username or user.email},</p>
        
        <p>Thank you for registering. Please confirm your email address by clicking the button below:</p>
        
        <p style="text-align: center;">
            <a href="{activation_link}" 
               style="background-color: #4CAF50; color: white; padding: 12px 20px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email
            </a>
        </p>
        
        <p>If the button doesn't work, copy and paste this link into your browser:</p>
        <p>{activation_link}</p>
        
        <hr>
        
        <p>If you didn't create an account, you can safely ignore this email.</p>
        
        <p>— The {project_name} Team</p>
    </body>
    </html>
    """


def get_registration_email_plain_text(user):
    activation_link = user.get_activation_link()
    project_name = settings.PROJECT_NAME

    return f"""Welcome to {project_name}!

Hi Test,

Thank you for registering. Please confirm your email address by opening the link below:

{activation_link}

If you didn't create an account, you can safely ignore this email.

— The {project_name} Team
"""


def get_registration_email_subject():
    from django.conf import settings

    return f"Verify your email - {settings.PROJECT_NAME}"


def send_registration_email(user):
    subject = get_registration_email_subject()
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    message = get_registration_email_plain_text(user)
    html_message = get_registration_email_html(user)

    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )


def format_offset(tz_name: str) -> str:
    now = datetime.now(ZoneInfo(tz_name))
    offset = now.utcoffset().total_seconds() / 3600

    sign = "+" if offset >= 0 else "-"
    return f"UTC{sign}{abs(offset):g}"


def get_continent(tz: str) -> str:
    # "Europe/Budapest" -> "Europe"
    return tz.split("/")[0] if "/" in tz else "Other"


def build_timezone_response():
    grouped = defaultdict(list)

    for tz in sorted(available_timezones()):
        if "/" not in tz:
            continue  # skip UTC, etc.

        continent = get_continent(tz)
        offset = format_offset(tz)

        grouped[continent].append(
            {
                "value": tz,
                "offset": offset,
            }
        )

    return grouped
