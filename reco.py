from common import db_manager
from common.util import utils
from common import mongo_manager

import random

class Reco:

    def __init__(self, jsonData, userInfo):
        self.jsonData = jsonData
        self.userInfo = userInfo

    def getRecoList(self):
        filteredList = self.getFilteredList()
        sortedList = self.sortListByScore(filteredList)

        #카테고리별로 분류해서 리턴하기
        return filteredList

    def getFilteredList(self):
        print("filtering")

        locationFilteredList = self.__getLocationFilteredList()
        timeFilteredList = self.__getTimeFilteredList(locationFilteredList)
        typeFilteredList = self.__getTypeFilteredList(timeFilteredList)

        return typeFilteredList

    #두 객체를 비교하는 함수
    def compareRank(self, objA, objB):
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
            originData['type_able_ing'] = random.choice([True, False])
            originData['type_able_after'] = random.choice([True, False])

        #score 계산
        featureList = []
        for originData in originList:
            originData['score'] = random.random()
        
        #정렬 
        for i in range(0, len(originList)):
            for j in range(i, len(originList)):
                if self.compareRank(originList[i], originList[j]):
                    tmp = originList[i]
                    originList[i] = originList[j]
                    originList[j] = tmp


        return originList

        
    def __getLocationFilteredList(self):
        locationList = self.jsonData['locations']
        
        # region에 입력된 값이 db에 존재하는지 체크해야하지 않을까?
        queryOptionParam = ", ".join("'%s'" % locationData['region'] for locationData in locationList)
        print(queryOptionParam)

        result = utils.fetch_all_json(
            db_manager.query(
                """
                SELECT reco_hashkey 
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
    print("hello")
    result = utils.fetch_all_json(
        db_manager.query(
            """
            SELECT * FROM USER ACCOUNT 
            WHERE is_active = %s
            """,
            (1,)
        )
    )

    print((result))
