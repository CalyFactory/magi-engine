from reco import Reco 
import json

with open('./jsonData.json') as conf_json:
    jsonData = json.load(conf_json)


recoModule = Reco(jsonData, None)

filteredList = recoModule.getFilteredList()

for listItem in filteredList:
    print(listItem)

print("=====================")
print(recoModule.getRecoList())
