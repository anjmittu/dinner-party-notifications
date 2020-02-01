import base64
from twilio.rest import Client
import os

def send_message(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    account_sid = os.getenv('ACCT_ID')
    auth_token = os.getenv('AUTH_TOK')
    client = Client(account_sid, auth_token)
    message_cook = "It is your turn to cook today.  Are you able to cook?"

    message = client.messages \
                    .create(
                         body=message_cook,
                         from_='+12029316658',
                         to=pubsub_message["to_number"]
                     )

    print(message.sid)
