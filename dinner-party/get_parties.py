from pymongo import MongoClient
import os
import time
from google.cloud import pubsub_v1
from typing import List
from datetime import datetime

def get_current_day():
    return datetime.today().weekday()

def get_cooker(people_table, people_ids: List):
    latest_cooked = None
    latest_person = None
    for person in people_ids:
        person_info = people_table.find_one({"_id": person})
        if latest_cooked is None or latest_cooked > person_info["last_cooked"]:
            # The person is current the last person to have cooked
            # We still need to check if they are able to cook today
            if get_current_day() in person_info["cook_days"]:
                latest_person = person_info
                latest_cooked = person_info["last_cooked"]
    return latest_person


def get_groups(request):
    # Set up Mongo DB
    client = MongoClient(os.getenv("MONGODB_URL"))
    db = client["diner-party"]
    parties = db["parties"]
    people = db["people"]
    # This will get all the parties
    cursor = parties.find({})

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
    for document in cursor:
        cooker = get_cooker(people, document["people"])

        if cooker is None:
            print("No one is able to cook")
            return

        data = cooker["number"]
        print("{} will be cooking".format())

        futures.update({data: None})

        future = publisher.publish(topic_path, data=data.encode("utf-8"))
        futures[data] = future

        future.add_done_callback(get_callback(future, data))
    
    while futures:
        time.sleep(5)

get_groups(None)