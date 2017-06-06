추천모듈 사용방법
---

추천 모듈 객체 생성!
```
recoModule = Reco(jsonData, None) 
```
첫번째 인자는 일정보강 모듈에서 받은 json데이터, 두번째 인자는 유저성향인데 현재 사용하지 않으니 None으로 넣으면 됩니다.

추천 데이터 가져오기!
```
recoModule.getRecoList()
```

