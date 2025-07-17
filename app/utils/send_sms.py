from unicodedata import name
from twilio.rest import Client
from django.conf import settings

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

def send_sms(to, name, message):
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    formatted_to = format_bangladesh_number(to)
    if not formatted_to:
        return False, "Invalid phone number format."

    final_message = f"👋 Hello, {name}\n{message}"
    try:
        client.messages.create(
            body=final_message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=formatted_to
        )
        return True, "Message sent successfully."
    except Exception as e:
        return False, str(e)

