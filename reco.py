from common import db_manager
from common.util import utils
from common import mongo_manager
import json
import re
import random
import math

class Reco:

    pricePriority = {
        'restaurant':67.3, 
        'cafe':41.1, 
        'place':57.4
    }
    distancePriority = {
        'restaurant':30.1, 
        'cafe':36.55, 
        'place':40.7
    }

    def __init__(self, jsonData, userInfo):
        self.jsonData = jsonData
        self.userInfo = userInfo

        self.initData()

    def initData(self):
        self.locationPriorityList = {}
        for locationData in self.jsonData['locations']:
            self.locationPriorityList[locationData['region']] = locationData['no']

        self.eventTypeIdList = []
        for eventType in self.jsonData['event_types']:
            self.eventTypeIdList.append(eventType['id'])
        
        priceList = utils.fetch_all_json(
            db_manager.query(
                """
                SELECT price 
                FROM RECOMMENDATION
                ORDER BY price 
                """
            )
        )

        distanceRowList = utils.fetch_all_json(
            db_manager.query(
                """
                SELECT distance 
                FROM RECOMMENDATION
                ORDER BY distance 
                """
            )
        )

        distanceList = []
        for distanceRow in distanceRowList:
            distanceString = re.search(r'\d+', distanceRow['distance'])
            if distanceString is None:
                distanceData = 99
            else:
                distanceData = int(distanceString.group())
            distanceList.append(distanceData)

        distanceList.sort()

        self.priceGradeList = []
        self.distanceGradeList = []

        n = 9

        for i in range(1, n + 1):
            position = int(self.getSNDPercent(n, i) * len(priceList)) - 1
            self.priceGradeList.append(priceList[position]['price'])

            position = int(self.getSNDPercent(n, i) * len(distanceList)) - 1
            self.distanceGradeList.append(distanceList[position])
            print(self.getSNDPercent(n, i))
        print(self.priceGradeList)
        print(self.distanceGradeList)

    def getSNDPercent(self, n, index):
        if n == index:
            return 1
        point = (index - n / 2) / 2
        score = self.__getSNDScore(point)
        return score
    
    def __getSNDScore(self, x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

    def getRecoList(self):
        #filteredList = self.getFilteredList()
        allList = self.getAllList()
        sortedList = self.sortListByScore(allList)

        #카테고리별로 분류해서 리턴하기
        return sortedList

    def getAllList(self):

        recoList = self.__getAllList()

        return recoList

    def getFilteredList(self):

        locationFilteredList = self.__getLocationFilteredList()
#        timeFilteredList = self.__getTimeFilteredList(locationFilteredList)
        typeFilteredList = self.__getTypeFilteredList(locationFilteredList)

        return typeFilteredList

    #두 객체의 우선순위 비교하는 함수
    #첫 번째 인자의 우선순위가 높을경우 True, 아닐경우 False 를 리턴함
    def isSecondArgHighPriority(self, itemA, itemB):

        if itemA['score'] < itemB['score']:
            return True 
        else:
            return False 

        #region
        itemARegionPriority = self.locationPriorityList[itemA['region']]
        itemBRegionPriority = self.locationPriorityList[itemB['region']]

        if itemARegionPriority < itemBRegionPriority:
            return False
        elif itemARegionPriority > itemBRegionPriority:
            return True

        #목적지표 event_type_availability
        ## TODO : 회의때 목적은 여러개인데 목적지표로 순위를 정하는것을 목적이 하나인 경우만 생각해서 정한 것 같다. 고민이 필요함

        eventTypeId = self.jsonData['event_types'][0]['id']

        itemAAvailabilityScore = self.__getAvailabilityScore(itemA, eventTypeId)
        itemBAvailabilityScore = self.__getAvailabilityScore(itemB, eventTypeId)

        if itemAAvailabilityScore > itemBAvailabilityScore:
            return False 
        elif itemAAvailabilityScore < itemBAvailabilityScore:
            return True 

        #score 
        itemAScore = itemA['score']
        itemBScore = itemB['score']

        if itemAScore < itemBScore:
            return False 
        elif itemAScore > itemBScore:
            return True 

        #등록된 시간 순서대로

        return True

        

    def __getAvailabilityScore(self, item, eventTypeId):

        #TODO : 테스트중이라 주석차리 하지만 eventTypeId가 없는경우가 존재해서는 안됨. 실제론 error를 내야함 
        if eventTypeId not in item['event_availability']:
            #raise Exception('no event_type_id in item')
            return 0 # 테스트 후 raise문을 사용할것
        
        ingValue = item['event_availability'][eventTypeId]['ing'] 

        return ingValue * 2 + afterValue

    def sortListByScore(self, originList):

        """
        랭킹 순위
        1. 장소
        2. 목적지표
        3. score (가격 + 거리)
        
        """

        #score 계산
        for row in originList:
            for originData in originList[row]:
                originData['score'] = self.__getScore(originData)
                
        #정렬 
        for row in originList:
            for i in range(0, len(originList[row])):
                for j in range(i, len(originList[row])):
                    if self.isSecondArgHighPriority(originList[row][i], originList[row][j]):
                        tmp = originList[row][i]
                        originList[row][i] = originList[row][j]
                        originList[row][j] = tmp
            for i in range(0, len(originList[row])):
                originList[row][i]['no'] = i
        
        #필터링 
        
        for row in originList:
            for originData in originList[row][:]:      
                if originData['score'] < 10000:
                    originList[row].remove(originData)

        return originList

    def getRange(self, array, value):
        for i in range(0, len(array)):
            if value<=array[i]:
                return i + 1
        return len(array)

    def __getScore(self, originData):

        score = 0

        #region 
        if originData['region'] in self.locationPriorityList:
            score += (10 - self.locationPriorityList[originData['region']]) * 10000

        #목적

        for i in range(0, len(self.eventTypeIdList)):
            eventTypeId = self.eventTypeIdList[i]
            ingValue = 1
            if eventTypeId in originData['event_availability']:
                ingValue = originData['event_availability'][eventTypeId]['ing']
            # ○ => 3   //*2000
            # △ => 2  //*1000
            # × => 1   //*0

            score += ((ingValue - 1) * 1000) 
        
        
        #가격

        priceData = originData['price']
        distanceString = re.search(r'\d+', originData['distance'])
        if distanceString is None:
            distanceData = 99
        else:
            distanceData = int(distanceString.group())
        
        priceRank = self.getRange(self.priceGradeList, priceData)
        distanceRank = self.getRange(self.distanceGradeList, distanceData)

        sumPriority = self.pricePriority[originData['category']] + self.distancePriority[originData['category']]
        pricePriority = self.pricePriority[originData['category']] / sumPriority
        distancePriority = self.distancePriority[originData['category']] / sumPriority

        score += (10 - (priceRank * pricePriority + distanceRank * distancePriority)) * 100

        return score

    def __getAllList(self):
        dataList = utils.fetch_all_json(    
            db_manager.query(
                """
                SELECT 
                    r.reco_hashkey, 
                    r.region, 
                    r.title,
                    r.price, 
                    r.distance,
                    r.category,
                    CONCAT(
                        "[",
                        GROUP_CONCAT(
                            JSON_OBJECT(
                                'id', etr.id,
                                'event_type_id', etr.event_type_id,
                                'ing', etr.ing
                            )
                        ),
                        "]"
                    ) as event_availability 
                FROM RECOMMENDATION as r
                LEFT JOIN EVENT_TYPE_RECO as etr
                ON
                    r.reco_hashkey = etr.reco_hashkey
                GROUP BY r.reco_hashkey
                """
            )
        )

        recoList = {
            'restaurant': [],
            'cafe': [],
            'place': []
        }

        for dataItem in dataList:
            recoList[dataItem['category']].append(dataItem)
        
        for dataItem in recoList:
        
            for recoItem in recoList[dataItem]:
                jsonConvertedItem = json.loads(recoItem['event_availability'])
                recoItem['event_availability'] = {}
                for jsonItem in jsonConvertedItem:
                    if jsonItem['event_type_id'] == None:
                        continue
                    recoItem['event_availability'][jsonItem['event_type_id']] = jsonItem
        
        return recoList

        
    def __getLocationFilteredList(self):
        locationList = self.jsonData['locations']
        
        # TODO : region에 입력된 값이 db에 존재하는지 체크해야하지 않을까?
        queryOptionParam = ", ".join("'%s'" % locationData['region'] for locationData in locationList)

        dataList = utils.fetch_all_json(
            db_manager.query(
                """
                SELECT 
                    r.reco_hashkey, 
                    r.region, 
                    r.title,
                    r.price, 
                    r.distance,
                    r.category,
                    CONCAT(
                        "[",
                        GROUP_CONCAT(
                            JSON_OBJECT(
                                'id', etr.id,
                                'event_type_id', etr.event_type_id,
                                'ing', etr.ing
                            )
                        ),
                        "]"
                    ) as event_availability 
                FROM RECOMMENDATION as r
                LEFT JOIN EVENT_TYPE_RECO as etr
                ON
                    r.reco_hashkey = etr.reco_hashkey
                WHERE
                    region IN (%s)
                GROUP BY r.reco_hashkey
                """ %
                queryOptionParam
            )
        )

        recoList = {
            'restaurant': [],
            'cafe': [],
            'place': []
        }

        for dataItem in dataList:
            recoList[dataItem['category']].append(dataItem)
        
        for dataItem in recoList:
        
            for recoItem in recoList[dataItem]:
                jsonConvertedItem = json.loads(recoItem['event_availability'])
                recoItem['event_availability'] = {}
                for jsonItem in jsonConvertedItem:
                    if jsonItem['event_type_id'] == None:
                        continue
                    recoItem['event_availability'][jsonItem['event_type_id']] = jsonItem
        
        return recoList

    def __getTimeFilteredList(self, originList):
        timeData = self.jsonData['time']
        return originList 

    def __getTypeFilteredList(self, originList):
        eventTypeData = self.jsonData['event_types']
        eventTypeId = self.jsonData['event_types'][0]['id']

        for row in originList:
            for originData in originList[row][:]:            
                if eventTypeId not in originData['event_availability']: 
                    #raise Exception('no event_type_id in item') #TODO : 테스트일때만 에러를 생략
                    ing = 0
                    after = 0
                else:
                    ing = originData['event_availability'][eventTypeId]['ing']
                    after = originData['event_availability'][eventTypeId]['after']

    #            if ing + after == 0: #TODO : 테스트 일때만 필터링을 안함
    #                originList.remove(originData)
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

