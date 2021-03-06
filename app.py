from reco import Reco
from common import db_manager
from common import mongo_manager
from common.util import utils
import json
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

with open('./jsonData.json') as conf_json:
    jsonData = json.load(conf_json)
"""
추천모듈 사용방법!!!

#추천 모듈 객체 생성!
recoModule = Reco(jsonData, None) #첫번째 인자는 일정보강 모듈에서 받은 json데이터, 두번째 인자는 유저성향인데 현재 사용하지 않으니 None으로 

#추천 데이터 가져오기!
recoModule.getRecoList()

끗!

"""



recoModule = Reco(jsonData, '2')



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
print(sortedList)