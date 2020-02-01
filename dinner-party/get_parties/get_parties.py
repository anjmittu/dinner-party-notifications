import os
import time
from google.cloud import pubsub_v1
from dinner_party_database.utils import Utils

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
            return

        data = cooker["number"]
        print("{} will be cooking".format(data))

        futures.update({data: None})

        future = publisher.publish(topic_path, data=data.encode("utf-8"))
        futures[data] = future

        future.add_done_callback(get_callback(future, data))
    
    while futures:
        time.sleep(5)

get_groups(None)