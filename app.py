from reco import Reco
from common import db_manager
from common import mongo_manager
from common.util import utils
import json
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

with open('./jsonData.json') as conf_json:
    json_data = json.load(conf_json)
    



reco_module = Reco(json_data)



"""
print("=====================")
print("filtered list")
print("=====================")
for category in filteredList:
    print("category : " + str(category))
    i=0
    for listItem in filteredList[category]:

        print(
            "[%2d] %5s %s"
            %
            (
                i,
                listItem['region'],
                listItem['title']
            )
        )
        i+=1
print("\n\n\n")
"""

print("=====================")
print("sorted list")
print("=====================")

sorted_list = reco_module.get_reco_list()
for category in sorted_list:
    print("category : " + str(category))
    i=0
    for item in sorted_list[category]:

        print(
            "[%2d] %5s %5d %s"
            %
            (
                i,
                item['region'],
                item['score'],
                item['title']
            )
        )
        i+=1