import requests

from celery import shared_task

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
    activation_link = 'http://165.22.29.172/login'
    subject = 'Activate your account'

    message = f'''
Hello {user.first_name or ''},

Thank you for registering.

To complete your account activation, please enter the activation code below on the activation page:

Activation Code:
{user.activation_code}

Open the activation page here:
{activation_link}

If you did not request this account, you can safely ignore this email.

Best regards,
Time Tracker System
'''.strip()


    send_email(
        user.email,
        subject,
        message,
    )

@shared_task
def send_reminder(email, first_name, last_name, missing_days, start_date, end_date):
    separator = '\n'
    lines = []

    for day in missing_days:
        lines.append(
            f"{day['date']} - missing {day['missing_hours']}h"
        )

    subject = 'Final Notice: Timesheet Submission Required'

    message = f'''
Dear {last_name} {first_name},

We noticed that your timesheet has missing or incomplete entries for the following period:

📅 Period: {start_date} – {end_date}
{separator.join(lines)}

This is a final notice that your timesheet remains incomplete.
Please be informed that timely submission of timesheets is mandatory for payroll processing. 
If your timesheet is not submitted by the required deadline, your salary payment will not be 
processed until the timesheet is duly completed, submitted, and approved.
No exceptions will be made.

Please complete and submit your timesheet immediately.

Best regards,
HR / Finance Department
'''

    send_email(
        email,
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