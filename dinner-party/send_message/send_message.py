import base64
from twilio.rest import Client
import os
from dinner_party_database.utils import Utils
import json

def send_message(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    json_str = base64.b64decode(event['data']).decode('utf-8')
    print(json_str)
    data = json.loads(json_str)
    number = data["number"]
    message = data["message"]
    last_question = data["last_question"]
    account_sid = os.getenv('ACCT_ID')
    auth_token = os.getenv('AUTH_TOK')
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body=message,
                         from_='+12029316658',
                         to=number
                     )

    print("phone: " + number)
    Utils.update_question(number, last_question)

    print(message.sid)
