from twilio.rest import Client
from loguru import logger
from dotenv import load_dotenv
import os


load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_VERIFIED_PHONE_NUMBER = os.getenv("TWILIO_VERIFIED_PHONE_NUMBER")

print(TWILIO_ACCOUNT_SID)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

call = client.calls.create(
    url="http://demo.twilio.com/docs/voice.xml",
    to=TWILIO_VERIFIED_PHONE_NUMBER,
    from_=TWILIO_PHONE_NUMBER,
)

logger.info(f"Call initiated: {call.sid}")
