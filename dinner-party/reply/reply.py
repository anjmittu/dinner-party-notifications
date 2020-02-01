from twilio.twiml.messaging_response import MessagingResponse
from urllib import parse
from dinner_party_database.utils import Utils
import dateparser
from google.cloud import pubsub_v1
import os
import time
import json


def reply(request):
    # Set up pub/sub system which will trigger other lambda
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(os.getenv("PROJECT_ID"), os.getenv("TOPIC_NAME"))
    futures = dict()

    def get_callback(f, data):
        def callback(f):
            try:
                print(f.result())
                futures.pop(data)
            except:  # noqa
                print("Please handle {} for {}.".format(f.exception(), data))

        return callback

    request_data = request.get_data()
    data_dict = dict(parse.parse_qsl(str(request_data)))

    from_number = data_dict["From"]
    reply_text = data_dict["Body"]

    # Start our response
    resp = MessagingResponse()

    last_question = Utils.get_last_question(from_number)

    if last_question == 1:
        if "yes" in reply_text.lower():
            # Updates who is cooking in the database
            Utils.update_event(
                Utils.get_event(from_number)["_id"],
                {"$set": {"who_cooking": Utils.get_person(from_number, {"_id": 1})["_id"]}}
            )
            resp.message("What is for dinner?")
            Utils.update_question(from_number, 2)
        if "no" in reply_text.lower():
            resp.message("Will you still be attending dinner?")
            Utils.update_question(from_number, 4)
            original_cook = Utils.get_person(from_number, {"_id": 1, "name":1})

            for person in Utils.get_party(from_number)["people"]:
                if person != original_cook["_id"]:
                    person_data = Utils.get_person_by_id(person, {"number": 1, "name": 1})
                    data = json.dumps({
                        "number": person_data["number"],
                        "message": "{} can not cook today.  Are you able to cook?".format(original_cook["name"]),
                        "last_question": 8
                    })
                    futures.update({data: None})
                    future = publisher.publish(topic_path, data=data.encode("utf-8"))
                    futures[data] = future
                    future.add_done_callback(get_callback(future, data))
            while futures:
                time.sleep(5)
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


    return str(resp)


