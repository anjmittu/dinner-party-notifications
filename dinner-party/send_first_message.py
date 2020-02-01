from twilio.rest import Client
import os

def send_message(request):
    request_json = request.get_json()
    account_sid = os.getenv('ACCT_ID')
    auth_token = os.getenv('AUTH_TOK')
    client = Client(account_sid, auth_token)
    message_cook = "It is your turn to cook today.  Are you still able to cook?"

    message = client.messages \
                    .create(
                         body=message_cook,
                         from_='+12029316658',
                         to=request_json["to_number"]
                     )

    print(message.sid)