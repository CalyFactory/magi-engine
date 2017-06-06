from reco import Reco
from common import db_manager
from common import mongo_manager
from common.util import utils
import json
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

with open('./jsonData.json') as conf_json:
    jsonData = json.load(conf_json)
    



recoModule = Reco(jsonData)



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

sortedList = recoModule.getRecoList()
for category in sortedList:
    print("category : " + str(category))
    i=0
    for listItem in sortedList[category]:

        print(
            "[%2d] %5s %5d %s"
            %
            (
                i,
                listItem['region'],
                listItem['score'],
                listItem['title']
            )
        )
        i+=1