from reco import Reco 
import json

with open('./jsonData.json') as conf_json:
    jsonData = json.load(conf_json)


recoModule = Reco(jsonData, None)
#print(recoModule.getFilteredList())

from common import mongo_manager

print(mongo_manager.event_log)