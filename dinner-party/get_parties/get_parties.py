import os
import time
from dinner_party_database.utils import Utils
import json

def get_groups(request):
    # This will get all the parties
    all_groups = Utils.get_all_party()


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

                Utils.trigger_function(data)
            return

        data = json.dumps({
            "number": cooker["number"],
            "message": "It is your turn to cook today.  Are you able to cook?",
            "last_question": 1
        })
        print("{} will be cooking".format(data))

        Utils.trigger_function(data)
    
