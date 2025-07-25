from unicodedata import name
from django.conf import settings
import requests

def format_bangladesh_number(number):
    # Ensure starts with +880
    if number.startswith('0'):
        return '+880' + number[1:]
    elif number.startswith('880'):
        return '+' + number
    elif number.startswith('+880'):
        return number
    else:
        return None  # invalid format



def send_sms(number, name, message):
    formatted_to = format_bangladesh_number(number)
    if not formatted_to:
        return False, "Invalid phone number format."

    final_message = f"Origin Acad\nDear {name}\n{message}"
    api_key = settings.SMS_API_KEY
    senderid = settings.SMS_SENDER_ID
    url = "http://bulksmsbd.net/api/smsapi"
    payload = {
        "api_key": api_key,       # Replace with your actual API key
        "senderid": senderid,    # Replace with your actual sender ID
        "number": formatted_to,
        "message": final_message
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return True, response.text
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)


# utils.py or inside views.py
def calculate_sms_segments(text):
    if len(text) <= 115:
        return 1
    else:
        return 1 + ((len(text) - 115 + 159) // 160)
    