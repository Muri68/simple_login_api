import requests
from django.conf import settings

def send_sms(phone_number, message):
    """
    Send SMS using Smart SMS Solution API
    """
    api_url = "https://app.smartsmssolutions.com/io/api/client/v1/sms/"
    
    params = {
        'token': settings.SMS_API_TOKEN,
        'sender': settings.SMS_SENDER_ID,
        'to': phone_number,
        'message': message,
        'type': '0',  # 0 for plain text
        'routing': '3'  # Route to Nigeria
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"SMS sending failed: {e}")
        return None