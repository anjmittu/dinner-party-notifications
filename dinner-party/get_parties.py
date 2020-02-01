from pymongo import MongoClient
from pprint import pprint
import os
import time
from google.cloud import pubsub_v1

def get_cooker(document):
    return document["people"][0]

def get_groups(request):
    client = MongoClient(os.getenv("MONGODB_URL"))
    db = client["diner-party"]
    parties = db["parties"]
    people = db["people"]
    cursor = parties.find({})

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

    for document in cursor:
        cooker = people.find_one({"_id": get_cooker(document)})

        data = cooker["number"]

        futures.update({data: None})

        future = publisher.publish(topic_path, data=data.encode("utf-8"))
        futures[data] = future

        future.add_done_callback(get_callback(future, data))
    
    while futures:
        time.sleep(5)

get_groups(None)