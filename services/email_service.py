import requests

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .microsoft_auth import get_access_token
from decouple import config


User = get_user_model()

def send_email(to_email, subject, body):
    access_token = get_access_token()

    url = f"https://graph.microsoft.com/v1.0/users/{config('MS_SENDER_EMAIL')}/sendMail"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    data = {
        'message': {
            'subject': subject,
            'body': {
                'contentType': 'Text',
                'content': body,
            },
            'toRecipients': [
                {
                    'emailAddress': {
                        'address': to_email
                    }
                }
            ],
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 202:
        raise Exception(response.text)

def send_activation_email(user):
    subject = 'Activate your account'

    message = f'''
Hello,

Your activation code is:

{user.activation_code}
'''

    send_email(
        user.email,
        subject,
        message,
    )

def send_reminder(email, start_date, end_date):
    user = User.objects.filter(email=email).first()

    if not user:
        return False

    subject = 'Reminder: Please complete your timesheet'

    message = f'''
Hello {user.first_name},

We noticed that your timesheet has missing or incomplete entries for the following period:

📅 Period: {start_date} – {end_date}

To ensure accurate reporting and avoid delays, please review and complete your missing working days as soon as possible.

If you have already submitted your entries, please disregard this message.

If you need assistance or believe this is an error, feel free to contact the support team.

Thank you for your cooperation.

Best regards,
Time Tracker System
'''

    send_email(
        user.email,
        subject,
        message,
    )

    return True

def send_message(email, subject, body):
    user = get_object_or_404(User, email=email)

    send_email(
        user.email,
        subject,
        body,
    )