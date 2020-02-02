# dinner-party-notifications

This project handles the text notifications for the dinner-party app.

The project runs on three different cloud functions:
* get_parties: This function runs once per day.  It kicks off the planning 
of the dinner.  For each part it will trigger send_message.

* send_message: This function will send a message to number given as input.
The input to this function is:
```
{
    "number": "the number the message should go to",
    "message": "the message to send",
    "last_question": "the number associated with the text being sent"
}
```

* reply: This handles the logic for when people reply to text.  Replies automatically
start the function.  Sometimes this function will call send_message to send messages
to other members of the party