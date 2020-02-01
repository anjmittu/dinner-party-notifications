from twilio.twiml.messaging_response import MessagingResponse
from urllib import parse
from dinner_party_database.utils import Utils
import dateparser


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
            Utils.update_event(
                Utils.get_event(from_number)["_id"],
                {"$set": {"who_cooking": Utils.get_person(from_number, {"_id": 1})["_id"]}}
            )
            resp.message("What is for dinner?")
            Utils.update_question(from_number, 2)
        if "no" in reply_text.lower():
            resp.message("Will you still be attending dinner?")
            Utils.update_question(from_number, 4)
    elif last_question == 2:
        Utils.update_event(
            Utils.get_event(from_number)["_id"],
            {"$set": {"whats_for_dinner": reply_text}}
        )

        resp.message("What time will dinner be ready? (HH:MM AM|PM)")
        Utils.update_question(from_number, 3)
    elif last_question == 3:
        #TODO: Send message with summary of dinner

        Utils.update_event(
            Utils.get_event(from_number)["_id"],
            {"$set": {"time": dateparser.parse(reply_text)}}
        )

        resp.message("Great, see you then!")
        Utils.update_question(from_number, 0)
    elif last_question == 4:
        if "yes" in reply_text.lower():
            resp.message("Alright we will update you when dinner plans are made")
            # TODO: message party
        if "no" in reply_text.lower():
            resp.message("Alright, maybe next time :(")


    # TODO: update the last question sent in the db

    return str(resp)


