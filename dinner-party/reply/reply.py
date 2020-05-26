from twilio.twiml.messaging_response import MessagingResponse
from urllib import parse
from dinner_party_database.utils import Utils
from dinner_party_database.response_utils import ResponseUtils as ru
import dateparser
import json

def found_cook(resp, cook_number):
    # Updates who is cooking in the database
    Utils.update_event(
        Utils.get_event(cook_number)["_id"],
        {"$set": {"who_cooking": Utils.get_person(cook_number, {"_id": 1})["_id"]}}
    )
    Utils.update_last_time_cooked(cook_number)
    resp.message("What is for dinner?")
    Utils.update_question(cook_number, 2)

def reply(request):
    # Start our response
    resp = MessagingResponse()

    request_data = request.get_data()
    data_dict = dict(parse.parse_qsl(str(request_data)))
    print(data_dict)

    from_number = data_dict["From"]
    reply_text = data_dict["Body"]

    last_question = Utils.get_last_question(from_number)
    print("last question: {}".format(last_question))

    reply_type = ru.response_sentiment(reply_text)

    if last_question == 1:
        if reply_type == 1:
            found_cook(resp, from_number)
            Utils.add_person_to_event(from_number)
        if reply_type == -1:
            resp.message("Alright I will update you when dinner plans are made")
            original_cook = Utils.get_person(from_number, {"_id": 1, "name":1})
            # Send a message to everyone else in the party to see if they can cook
            for person in Utils.get_party(from_number)["people"]:
                if person != original_cook["_id"]:
                    person_data = Utils.get_person_by_id(person, {"number": 1, "name": 1})
                    Utils.trigger_function(json.dumps({
                        "number": person_data["number"],
                        "message": "{} can not cook today.  Are you able to cook?".format(original_cook["name"]),
                        "last_question": 8
                    }))

    elif last_question == 2:
        if reply_type == 0:
            resp.message("I'll ask the other for suggestions.  Reply back whenever you decide.")

            original_cook = Utils.get_person(from_number, {"_id": 1, "name": 1})
            # Send a message to everyone else in the party to see if they can cook
            for person in Utils.get_party(from_number)["people"]:
                if person != original_cook["_id"]:
                    person_data = Utils.get_person_by_id(person, {"number": 1, "name": 1})
                    Utils.trigger_function(json.dumps({
                        "number": person_data["number"],
                        "message": "{} is cooking today.  Do you have any suggestions for dinner?".format(original_cook["name"]),
                        "last_question": 10
                    }))
        else:
            Utils.update_event(
                Utils.get_event(from_number)["_id"],
                {"$set": {"whats_for_dinner": reply_text}}
            )

            resp.message("What time will dinner be ready? (HH:MM AM|PM)")
            Utils.update_question(from_number, 3)
    elif last_question == 3:
        Utils.update_event(
            Utils.get_event(from_number)["_id"],
            {"$set": {"time": dateparser.parse(reply_text)}}
        )

        resp.message("Great, see you then!")
        Utils.update_question(from_number, 0)

        people = Utils.get_party(from_number)["people"]
        cook = Utils.get_person(from_number, {"_id": 1, "name": 1})
        event = Utils.get_event(from_number)
        dinner_time = event["time"].strftime("%I:%M %p")

        resp = "{} is cooking {} for dinner. Dinner will be at {}.  Will you be there?".format(cook["name"], event["whats_for_dinner"], dinner_time)

        for person in people:
            if person != cook["_id"]:
                number = Utils.get_person_by_id(person, {"number": 1})["number"]
                Utils.trigger_function(json.dumps({
                    "number": number,
                    "message": resp,
                    "last_question": 5
                }))

    elif last_question == 5:
        if reply_type == 1:
            resp.message("Great, see you then!")
            Utils.add_person_to_event(from_number)
            Utils.update_question(from_number, 0)
        if reply_type == -1:
            resp.message("Alright, maybe next time :(")
            Utils.remove_person_to_event(from_number)
            Utils.update_question(from_number, 0)
        if Utils.check_if_everyone_respond(from_number) and last_question == 5:
            if Utils.is_anyone_coming(from_number):
                for person in Utils.people_who_come(from_number):
                    number = Utils.get_person_by_id(person, {"number": 1})["number"]
                    Utils.trigger_function(json.dumps({
                        "number": number,
                        "message": "{} will all be coming for dinner".format(Utils.get_list_people_coming(from_number)),
                        "last_question": 5
                    }))
    elif last_question == 8 or last_question == 9:
        if reply_type == 1:
            if not Utils.is_there_a_cook(from_number):
                found_cook(resp, from_number)
                Utils.add_person_to_event(from_number)
            else:
                resp.message("Someone has already said they will cook.  I will update you when dinner plans ready.")
        if reply_type == -1:
            if last_question == 9:
                resp.message("Alright, maybe next time :(")
                Utils.remove_person_to_event(from_number)
                Utils.update_question(from_number, 0)

            if Utils.check_if_everyone_respond(from_number):
                if not Utils.is_anyone_coming(from_number):
                    for person in Utils.get_party(from_number)["people"]:
                        person_data = Utils.get_person_by_id(person, {"number": 1, "name": 1})
                        Utils.trigger_function(json.dumps({
                            "number": person_data["number"],
                            "message": "There is no one who can cook dinner today",
                            "last_question": 0
                        }))

    elif last_question == 10:
        Utils.trigger_function(json.dumps({
            "number": Utils.get_cook(from_number)["number"],
            "message": "{} suggests {}".format(Utils.get_person(from_number, {"name":1})["name"], reply_text),
            "last_question": 2
        }))


    return str(resp)


