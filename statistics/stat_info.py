import pandas as pd
import os
from datetime import date
from common import component, info
from extractor import mt
import exception
pd.set_option('mode.chained_assignment',  None)

docPath = '../doc/'
chargerFile = 'charger_list.csv'
# historyFile = 'charger_usage_history.csv'
chargerStatList = 'charger_stat_list.csv'

if not os.path.isfile(docPath + chargerFile):
    raise exception.FileExistException
else:
    charger_list = pd.read_csv(docPath + chargerFile)
    # history = pd.read_csv(docPath + historyFile)

# 사용이력 DB
history = mt.select_usage(info.table[2])

# 급속 충전기 추출
dc_chargers = charger_list[charger_list['chargerType'] == info.charger_type[1]]
# 사용내역 목록
history['chStartTm'] = pd.to_datetime(history['chStartTm'], format='%Y-%m-%d %H:%M:%S')
history['chEndTm'] = pd.to_datetime(history['chEndTm'], format='%Y-%m-%d %H:%M:%S')
# history['totEnergy'] = history['totEnergy'].apply(lambda x: x.replace(',', '')).astype('int64')

filterCol = ["chId", "placeName", "evseId", "evseName", "chStartTm", "chEndTm", "memberNo", "nonMemberNo",
             "userName", "chTm2", "totEnergy", "payCost", "totCost", "rmCardEntity", "stoppedReason"]
history = history[filterCol].reset_index(drop=True)

start_date = date(2022, 4, 1)
chargerHistory = mt.select_time(history, 'chStartTm', start_date, 3)
chargerHistory = chargerHistory[chargerHistory['totEnergy'] > 0]           # 충전량 > 0
chargerHistory = chargerHistory.dropna(subset=['chStartTm', 'chEndTm'])

# 기간, 회원타입 컬럼 추가
comp = component.base(chargerHistory)
chargerHistory = comp.add_columns()

# 사용내역 충전소 목록
historyStation = chargerHistory.drop_duplicates(['placeName', 'evseId'], keep='first')
historyStation = historyStation[['placeName', 'evseId']].sort_values(by=['placeName', 'evseId']).reset_index(drop=True)

# 사용내역과 통계정보에 속한 충전기
# existStations = dc_chargers[dc_chargers['station_name'].isin(historyStation['station_name'])].reset_index(drop=True).sort_values(by=['station_name', 'charger_id'])
# print(f'New Stations corresponding DB: {len(existStations)}')

existStations = historyStation
chargerStat = []

for n in range(len(existStations)):
    placeName = historyStation.iloc[n, 0]
    evseId = int(historyStation.iloc[n, 1])
    print(f"{n} place: {placeName} / evse id: {evseId}")

    # 신규 충전기 = 충전소이름 + 충전기코드(charger_id)
    addCharger = existStations.where((existStations['placeName'] == placeName) & (existStations['evseId'] == evseId)).dropna()
    addCharger = addCharger.astype({'evseId': int})

    selectStation = chargerHistory[(chargerHistory['placeName'] == placeName) & (chargerHistory['evseId'] == evseId)].reset_index(drop=True)
    weekdayAvgStat = comp.charger_avg_stat(selectStation, 'weekday')
    weekdayHourStat = comp.charger_avg_stat(selectStation, 'weekday', 'hour')
    isweekAvgStat = comp.charger_avg_stat(selectStation, 'isWeek')
    monthlyAvgStat = comp.charger_avg_stat(selectStation, 'month')

    # 일 평균 이용률
    addCharger['utz'] = round(isweekAvgStat['utz'].mean(), 1)
    addCharger['monthlyUtz'] = round(monthlyAvgStat['utz'].mean(), 1)

    # 평균 통계값
    addCharger['avgChTm'] = round(selectStation['chTm2'].mean() / 60, 1)
    addCharger['avgTotEnergy'] = round(selectStation['totEnergy'].mean(), 1)

    monDict = {}
    tueDict = {}
    wedDict = {}
    thuDict = {}
    friDict = {}
    satDict = {}
    sunDict = {}

    weekdays = weekdayAvgStat['weekday']
    for n in range(len(weekdays)):
        valList = []
        keyList = ['weekday', 'utz', 'rank', 'dawnUtz', 'amUtz', 'pmUtz', 'nightUtz']

        weekday = weekdayAvgStat['weekday'][n] # 요일
        utz = weekdayAvgStat['utz'][n] # 요일 이용률
        rank = comp.utilization_group(utz)[0] # 요일 이용률 그룹
        dawnUtz = comp.tz_util(weekdayHourStat, weekday, info.dc_tz[0]) # 새벽 이용률
        amUtz = comp.tz_util(weekdayHourStat, weekday, info.dc_tz[1]) # 오전 이용률
        pmUtz = comp.tz_util(weekdayHourStat, weekday, info.dc_tz[2]) # 오후 이용률
        nightUtz = comp.tz_util(weekdayHourStat, weekday, info.dc_tz[3]) # 밤 이용률

        valList.append(weekday)
        valList.append(utz)
        valList.append(rank)
        valList.append(dawnUtz)
        valList.append(amUtz)
        valList.append(pmUtz)
        valList.append(nightUtz)

        if weekday == 0:
            monDict = dict(zip(keyList, valList))
        elif weekday == 1:
            tueDict = dict(zip(keyList, valList))
        elif weekday == 2:
            wedDict = dict(zip(keyList, valList))
        elif weekday == 3:
            thuDict = dict(zip(keyList, valList))
        elif weekday == 4:
            friDict = dict(zip(keyList, valList))
        elif weekday == 5:
            satDict = dict(zip(keyList, valList))
        else:
            sunDict = dict(zip(keyList, valList))
    # 요일별-시간대별 이용률 json 형태로 저장
    addCharger['monUtz'] = str(monDict)
    addCharger['tueUtz'] = str(tueDict)
    addCharger['wedUtz'] = str(wedDict)
    addCharger['thuUtz'] = str(thuDict)
    addCharger['friUtz'] = str(friDict)
    addCharger['satUtz'] = str(satDict)
    addCharger['sunUtz'] = str(sunDict)

    chargerStat.append(addCharger)  # 충전기 통계정보 추가
    print("New charger is registered\n")

stations = pd.concat(chargerStat).sort_values(by=['placeName', 'evseId'])
stations.to_csv(docPath + chargerStatList, index=False, encoding='utf-8')