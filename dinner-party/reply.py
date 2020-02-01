from twilio.twiml.messaging_response import MessagingResponse
from urllib import parse
from dinner_party_database.utils import Utils


def reply(request):
    request_data = request.get_data()
    data_dict = dict(parse.parse_qsl(str(request_data)))

    from_number = data_dict["From"]
    reply_text = data_dict["Body"]

    # Start our response
    resp = MessagingResponse()

    last_question = Utils.get_last_question(from_number)
    print(last_question)

    if last_question == 1:
        if "yes" in reply_text.lower():
            # Add a message
            update_event(
                get_event(from_number),
                {"$set": {"who_cooking": get_person(from_number, {"_id": 1})["_id"]}}
            )
            Utils.get_person(from_number)
            resp.message("What is for dinner?")
            # TODO: save cook info in current dinner event
        if "no" in reply_text.lower():
            resp.message("Will you still be attending dinner?")
    elif last_question == 2:
        resp.message("What time will dinner be ready?")
        # TODO: save the response to the current dinner event in db
    elif last_question == 3:
        #TODO: Send message with summary of dinner
        resp.message("Great, see you then!")
    elif last_question == 4:
        if "yes" in reply_text.lower():
            resp.message("Alright we will update you when dinner plans are made")
            # TODO: message party
        if "no" in reply_text.lower():
            resp.message("Alright, maybe next time :(")

    # TODO: update the last question sent in the db

    return str(resp)


