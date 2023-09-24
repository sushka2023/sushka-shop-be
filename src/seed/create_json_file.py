import json
from data_module import data_json


def create_json_data():
    with open("data.json", "w") as json_file:
        json.dump(data_json, json_file, indent=4)
