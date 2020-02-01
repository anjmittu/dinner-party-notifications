import os
import time
from google.cloud import pubsub_v1
from dinner_party_database.utils import Utils
import json

def get_groups(request):
    # This will get all the parties
    all_groups = Utils.get_all_party()

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

    # Loops through each party
    for party in all_groups:
        cooker = Utils.get_cooker(party["people"])

        if cooker is None:
            print("No one is able to cook")
            for person in party["people"]:
                data = json.dumps({
                    "number": Utils.get_person_by_id(person)["number"],
                    "message": "No one can cook today.  Are you able to cook?",
                    "last_question": 9
                })

                futures.update({data: None})

                future = publisher.publish(topic_path, data=data.encode("utf-8"))
                futures[data] = future

                future.add_done_callback(get_callback(future, data))
            return

        data = json.dumps({
            "number": cooker["number"],
            "message": "It is your turn to cook today.  Are you able to cook?",
            "last_question": 1
        })
        print("{} will be cooking".format(data))

        futures.update({data: None})

        future = publisher.publish(topic_path, data=data.encode("utf-8"))
        futures[data] = future

        future.add_done_callback(get_callback(future, data))
    
    while futures:
        time.sleep(5)

get_groups(None)