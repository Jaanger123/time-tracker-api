from decouple import config
import requests


def get_access_token():
    url = f"https://login.microsoftonline.com/{config('MS_TENANT_ID')}/oauth2/v2.0/token"

    data = {
        'client_id': config('MS_CLIENT_ID'),
        'client_secret': config('MS_CLIENT_SECRET'),
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    return response.json()['access_token']