# from django.core.mail import send_mail
# from django.conf import settings


# def send_activation_email(user):
#     subject = 'Activate your account'

#     message = f'''
# Hello,

# Your activation code is:

# {user.activation_code}
# '''

#     send_mail(
#         subject,
#         message,
#         settings.EMAIL_HOST_USER,
#         [user.email],
#         fail_silently=False,
#     )


import requests
from config.decouple_config import config
from .microsoft_auth import get_access_token


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
