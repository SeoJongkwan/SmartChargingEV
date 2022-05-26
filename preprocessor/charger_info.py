import pandas as pd
import numpy as np
from datetime import date
import os
from common import component, info
from extractor import mt
pd.set_option('mode.chained_assignment',  None)

doc_path = '../doc/'
registeredCharger = 'regStations.csv'
chargerList = 'charger_list.csv'

# get_regStations = mt.all_stations()                                       #DB 등록된 충전소 최초 1회 load
# get_regStations.to_csv(doc_path + registeredCharger, index=False, encoding='cp949')
regStations = pd.read_csv(doc_path + registeredCharger, encoding='cp949')
print(f'Registered Charger: {len(regStations)}')

usageHistory = pd.read_csv(doc_path + 'charger_usage_history.csv')          #충전기 사용내역 load
usageHistory['start_time'] = pd.to_datetime(usageHistory['start_time'], format='%Y-%m-%d %H:%M:%S')
usageHistory['end_time'] = pd.to_datetime(usageHistory['end_time'], format='%Y-%m-%d %H:%M:%S')
usageHistory['charging_capacity'] = usageHistory['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')

filterColumn = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number",
                "member_name", "charging_time", "charging_capacity", "paid_fee","charging_fee","roaming_card_entity","charging_status"]
filterCharger = usageHistory[filterColumn].reset_index(drop=True)

startDate = date(2022, 1, 1)                                                #2022년 기간설정
chargerHistory = mt.select_time(filterCharger, 'start_time', startDate, 4)
charger = chargerHistory[chargerHistory['charging_capacity'] > 0]           # 충전량 > 0
charger = charger.dropna(subset=['start_time', 'end_time'])
print(f'Registered Usage History: {len(usageHistory)} (Capacity>0): {len(charger)}')

# 충전시간(seconds), 주중/주말 구분
component = component.base(charger)
charger = component.time_split('start_time')
charger['chargingTime'] = (charger['end_time'] - charger['start_time']).dt.total_seconds()
charger = charger.astype({'chargingTime': int})
charger['isWeek'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)

# 신규 충전소 목록
newStations = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')
newStations = newStations[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

exStations = regStations[regStations['station_name'].isin(newStations['station_name'])].reset_index(drop=True)
print(f'New Stations corresponding DB: {len(exStations)}')

chargerCheck = []                                                           #신규츙전소 저장 리스트
# n = 2
for n in range(len(exStations)):
    stationName = exStations.iloc[n, 1]
    chargerId = exStations.iloc[n, 2]
    print(f"{n} station: {stationName} / charger id: {chargerId}")
    selectStation = charger[charger['station_name'] == stationName].reset_index(drop=True)
    selectCharger = selectStation[selectStation['charger_code'] == chargerId].reset_index(drop=True)
    if selectCharger.empty:
        print("There are Station but, no Charger ID\n")                               #DB에는 충전기코드가 등록되어 있지만 신규 파일에는 없음
    else:
        selectCharger['paid_fee'] = selectCharger['paid_fee'].apply(lambda x: x.replace(',', '')).astype('int')
        selectCharger['charging_fee'] = selectCharger['charging_fee'].apply(lambda x: x.replace(',', '')).astype('int')

        #신규 충전기 = 충전소이름 + 충전기코드(charger_id)
        newCharger = exStations.where((exStations['station_name'] == stationName) & (exStations['charger_id'] == chargerId)).dropna()
        newCharger = newCharger.astype({'charger_id': int})
        newCharger['chargerType'] = info.charger_type[1]
        newCharger['chargerPlace'] = info.charger_place[0]
        newCharger['chargerOpTIme'] = info.charger_opTime[0]
        newCharger['chargerTarget'] = info.charger_target[0]

        # monthly_avg_stat = component.charger_avg_stat(selectCharger, 'month')
        # weekday_avg_stat = component.charger_avg_stat(selectCharger, 'weekday')
        # daily_avg_stat = component.charger_avg_stat(selectCharger, 'date')
        hourly_avg_stat = component.charger_avg_stat(selectCharger, 'hour')
        isweek_occp_stat = component.charger_avg_stat(selectCharger, 'isWeek', 'date')
        isweek_avg_stat = component.charger_avg_stat(selectCharger, 'isWeek', 'hour')
        isweek_hour_stat = component.charger_avg_stat(selectCharger, 'date', 'isWeek', 'hour')

        #주중/주말 평균 이용률
        weekType = isweek_occp_stat.groupby(['isWeek']).mean().reset_index()
        if len(weekType) == 2:
            newCharger['wdUtilization'] = round(weekType.iloc[0]['utilization'], 2)
            newCharger['wkndUtilization'] = round(weekType.iloc[1]['utilization'], 2)
        elif len(weekType) == 1 and weekType.iloc[0]['isWeek'] == 0:
            newCharger['wdUtilization'] = round(weekType.iloc[0]['utilization'], 2)
            newCharger['wkndUtilization'] = 0
        elif len(weekType) == 1 and weekType.iloc[0]['isWeek'] == 1:
            newCharger['wdUtilization'] = 0
            newCharger['wkndUtilization'] = round(weekType.iloc[0]['utilization'], 2)
        else:
            print("No weekType")


        #주중/주말 최대,최소 충전시간(criteria 변수를 통해 시간대 개수 정의)
        criteria = 5
        weekMax = isweek_avg_stat[isweek_avg_stat['isWeek'] == 0].sort_values(by='utilization', ascending=False).head(criteria)
        weekMin = isweek_avg_stat[isweek_avg_stat['isWeek'] == 0].sort_values(by='utilization', ascending=True).head(criteria)
        weekendMax = isweek_avg_stat[isweek_avg_stat['isWeek'] == 1].sort_values(by='utilization', ascending=False).head(criteria)
        weekendMin = isweek_avg_stat[isweek_avg_stat['isWeek'] == 1].sort_values(by='utilization', ascending=True).head(criteria)

        newCharger['wdMaxHour'] = str(weekMax['hour'].values)
        newCharger['wdMinHour'] = str(weekMin['hour'].values)
        newCharger['wkndMaxHour'] = str(weekendMax['hour'].values)
        newCharger['wkndMinHour'] = str(weekendMin['hour'].values)

        #주중/주말 최대,최소 충전시간대
        # newCharger['wdMaxTz'] = component.timezone_classification(weekMax, 'max')
        # newCharger['wdMinTz'] = component.timezone_classification(weekMin, 'min')
        # newCharger['wkndMaxTz'] = component.timezone_classification(weekendMax, 'max')
        # newCharger['wkndMinTz'] = component.timezone_classification(weekendMin, 'min')

        #평균 통계값
        newCharger['avgChargeTime'] = round(selectCharger['chargingTime'].mean() / 60, 2)
        newCharger['avgChargeCap'] = round(selectCharger['charging_capacity'].mean(), 2)

        chargerCheck.append(newCharger)                                                 #신규 충전기 추가
        print("New charger is registered\n")



stations = pd.concat(chargerCheck)
# 충전기 이용률 그룹화
stations.insert(9, 'wdrank', component.utilization_group(stations['wdUtilization']))
stations.insert(11, 'wkndrank', component.utilization_group(stations['wkndUtilization']))
stations.to_csv(doc_path + chargerList, index=False, encoding='utf-8')
