from common import db_manager
from common.util import utils

class Reco:

    def __init__(self, jsonData, userInfo):
        self.jsonData = jsonData
        self.userInfo = userInfo

    def getRecoList(self):
        filteredList = self.getFilteredList()
        sortedList = self.sortListByScore(filteredList)
        return filteredList

    def getFilteredList(self):
        print("filtering")

        locationFilteredList = self.__getLocationFilteredList()
        timeFilteredList = self.__getTimeFilteredList(locationFilteredList)
        typeFilteredList = self.__getTypeFilteredList(timeFilteredList)

        return typeFilteredList

    def sortListByScore(self, originList):

        """
        랭킹에 사용될 feature
            추천 아이템의 클릭수
            유저들이 이 아이템의 블로그를 본 시간
            유저들이 이 아이템의 지도를 본 시간
            유저들이 이 아이템을 공유한 수 
            유저 모듈에서 가져온 유저의 성향

        
        """

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
