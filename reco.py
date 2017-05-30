from common import db_manager
from common.util import utils
from common import mongo_manager

import random

class Reco:

    def __init__(self, jsonData, userInfo):
        self.jsonData = jsonData
        self.userInfo = userInfo

        self.initData()

    def initData(self):
        self.locationPriorityList = {}
        for locationData in self.jsonData['locations']:
            self.locationPriorityList[locationData['region']] = locationData['no']

    def getRecoList(self):
        filteredList = self.getFilteredList()
        sortedList = self.sortListByScore(filteredList)

        #카테고리별로 분류해서 리턴하기
        return filteredList

    def getFilteredList(self):

        locationFilteredList = self.__getLocationFilteredList()
#        timeFilteredList = self.__getTimeFilteredList(locationFilteredList)
        typeFilteredList = self.__getTypeFilteredList(locationFilteredList)

        return typeFilteredList

    #두 객체의 우선순위 비교하는 함수
    #첫 번째 인자의 우선순위가 높을경우 True, 아닐경우 False 를 리턴함
    def isFirstArgHighPriority(self, itemA, itemB):

        #region
        itemARegionPriority = self.locationPriorityList[itemA['region']]
        itemBRegionPriority = self.locationPriorityList[itemB['region']]

        if itemARegionPriority < itemBRegionPriority:
            return False
        elif itemARegionPriority > itemBRegionPriority:
            return True

        #목적지표 event_type_availability
        ## TODO : 회의때 목적은 여러개인데 목적지표로 순위를 정하는것을 목적이 하나인 경우만 생각해서 정한 것 같다. 고민이 필요함

        eventTypeId = self.jsonData['eventType'][0]['typeId']

        itemAAvailabilityScore = itemA['event_type_availability'][eventTypeId]['int'] * 2 + itemA['event_type_availability'][eventTypeId]['after']
        itemBAvailabilityScore = itemB['event_type_availability'][eventTypeId]['int'] * 2 + itemB['event_type_availability'][eventTypeId]['after']

        if itemAAvailabilityScore < itemBAvailabilityScore:
            return False 
        elif itemARegionPriority > itemBRegionPriority:
            return True 

        return True

    def sortListByScore(self, originList):

        """
        랭킹 순위
        1. 장소
        2. 목적지표
        3. score (가격 + 거리)
        
        """

        #목적지표가 아직 db에 없기에 랜덤으로 만들어주는 부분
        for originData in originList:
            originData['event_type_availability'] = {}
            for i in range(0,9):
                originData['event_type_availability'][i] = {
                    'ing' :random.choice([True, False]),
                    'after' :random.choice([True, False])
                }
            print(originData)
        
        #score 계산
        for originData in originList:
            originData['score'] = random.random()
        
        #정렬 
        for i in range(0, len(originList)):
            for j in range(i, len(originList)):
                if self.isFirstArgHighPriority(originList[i], originList[j]):
                    tmp = originList[i]
                    originList[i] = originList[j]
                    originList[j] = tmp


        return originList

        
    def __getLocationFilteredList(self):
        locationList = self.jsonData['locations']
        
        # TODO : region에 입력된 값이 db에 존재하는지 체크해야하지 않을까?
        queryOptionParam = ", ".join("'%s'" % locationData['region'] for locationData in locationList)

        result = utils.fetch_all_json(
            db_manager.query(
                """
                SELECT reco_hashkey, region, title 
                FROM RECOMMENDATION
                WHERE
                    region IN (%s) 
                """ %
                queryOptionParam
            )
        )

        return result

    def __getTimeFilteredList(self, originList):
        timeData = self.jsonData['time']
        return originList 

    def __getTypeFilteredList(self, originList):
        eventTypeData = self.jsonData['eventType']
        return originList

def hello():
    result = utils.fetch_all_json(
        db_manager.query(
            """
            SELECT * FROM USER ACCOUNT 
            WHERE is_active = %s
            """,
            (1,)
        )
    )

