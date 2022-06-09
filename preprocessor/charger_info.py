import pandas as pd
import numpy as np
from datetime import date
import os
from common import component, info
from extractor import mt
from chart import charger as charger_chart
pd.set_option('mode.chained_assignment',  None)

DocPath = '../doc/'
RegisteredCharger = 'regStations.csv'
ChargerList = 'charger_list.csv'

# DBStations = mt.all_stations()                                       #DB 등록된 충전소 최초 1회 load
# DBStations.to_csv(DocPath + RegisteredCharger, index=False, encoding='cp949')
RegStations = pd.read_csv(DocPath + RegisteredCharger, encoding='cp949')
print(f'Registered Charger: {len(RegStations)}')

UsageHistory = pd.read_csv(DocPath + 'charger_usage_history.csv')          #충전기 사용내역 load
UsageHistory['start_time'] = pd.to_datetime(UsageHistory['start_time'], format='%Y-%m-%d %H:%M:%S')
UsageHistory['end_time'] = pd.to_datetime(UsageHistory['end_time'], format='%Y-%m-%d %H:%M:%S')
UsageHistory['charging_capacity'] = UsageHistory['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')

FilterColumn = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number",
                "member_name", "charging_time", "charging_capacity", "paid_fee","charging_fee","roaming_card_entity","charging_status"]
FilterCharger = UsageHistory[FilterColumn].reset_index(drop=True)

StartDate = date(2022, 1, 1)                                                #2022년 기간설정
ChargerHistory = mt.select_time(FilterCharger, 'start_time', StartDate, 4)
charger = ChargerHistory[ChargerHistory['charging_capacity'] > 0]           # 충전량 > 0
charger = charger.dropna(subset=['start_time', 'end_time'])
print(f'Registered Usage History: {len(UsageHistory)} (Capacity>0): {len(charger)}')

# 충전시간(seconds), 주중/주말 구분
comp = component.base(charger)
charger = comp.time_split('start_time')
charger['chargingTime'] = (charger['end_time'] - charger['start_time']).dt.total_seconds()
charger = charger.astype({'chargingTime': int})
charger['isWeek'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)

# 신규 충전소 목록
NewStations = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')
NewStations = NewStations[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

ExistStations = RegStations[RegStations['station_name'].isin(NewStations['station_name'])].reset_index(drop=True)
print(f'New Stations corresponding DB: {len(ExistStations)}')

ChargerCheck = []                                                           #신규츙전소 저장 리스트
# n = 2
for n in range(len(ExistStations)):
# for n in range(20, 30):
    StationName = ExistStations.iloc[n, 1]
    ChargerId = ExistStations.iloc[n, 2]
    print(f"{n} station: {StationName} / charger id: {ChargerId}")
    SelectStation = charger[charger['station_name'] == StationName].reset_index(drop=True)
    SelectCharger = SelectStation[SelectStation['charger_code'] == ChargerId].reset_index(drop=True)
    if SelectCharger.empty:
        print("There are Station but, no Charger ID\n")                               #DB에는 충전기코드가 등록되어 있지만 신규 파일에는 없음
    else:
        SelectCharger['paid_fee'] = SelectCharger['paid_fee'].apply(lambda x: x.replace(',', '')).astype('int')
        SelectCharger['charging_fee'] = SelectCharger['charging_fee'].apply(lambda x: x.replace(',', '')).astype('int')

        #신규 충전기 = 충전소이름 + 충전기코드(charger_id)
        NewCharger = ExistStations.where((ExistStations['station_name'] == StationName) & (ExistStations['charger_id'] == ChargerId)).dropna()
        NewCharger = NewCharger.astype({'charger_id': int})
        NewCharger['chargerType'] = info.charger_type[1]
        NewCharger['chargerPlace'] = info.charger_place[0]
        NewCharger['chargerOpTIme'] = info.charger_opTime[0]
        NewCharger['chargerTarget'] = info.charger_target[0]

        MonthlyAvgStat = comp.charger_avg_stat(SelectCharger, 'month', 'date')
        # WeekdayAvgStat = comp.charger_avg_stat(select_charger, 'weekday')
        # DailyAvgStat = comp.charger_avg_stat(select_charger, 'date')
        HourlyAvgStat = comp.charger_avg_stat(SelectCharger, 'date', 'hour')
        IsweekOccpStat = comp.charger_avg_stat(SelectCharger, 'isWeek', 'date')
        IsweekAvgStat = comp.charger_avg_stat(SelectCharger, 'isWeek', 'hour')
        IsweekHourStat = comp.charger_avg_stat(SelectCharger, 'date', 'isWeek', 'hour')

        # 이용률과 충전횟수
        # HourlyAvgStat['charging_time'] = round(HourlyAvgStat['chargingTime'] / 60, 2)
        # charger_chart = charger_chart.Plot(HourlyAvgStat)
        # charger_chart.show_occupation_cap(HourlyAvgStat, 'hour', station_name)

        #주중/주말 평균 이용률
        WeekType = IsweekOccpStat.groupby(['isWeek']).mean().reset_index()
        if len(WeekType) == 2:
            NewCharger['wdUtilization'] = round(WeekType.iloc[0]['utilization'], 2)
            NewCharger['wkndUtilization'] = round(WeekType.iloc[1]['utilization'], 2)
        elif len(WeekType) == 1 and WeekType.iloc[0]['isWeek'] == 0:
            NewCharger['wdUtilization'] = round(WeekType.iloc[0]['utilization'], 2)
            NewCharger['wkndUtilization'] = 0
        elif len(WeekType) == 1 and WeekType.iloc[0]['isWeek'] == 1:
            NewCharger['wdUtilization'] = 0
            NewCharger['wkndUtilization'] = round(WeekType.iloc[0]['utilization'], 2)
        else:
            print("No weekType")


        #주중/주말 최대,최소 충전시간(criteria 변수를 통해 시간대 개수 정의)
        criteria = 5
        WeekMax = IsweekAvgStat[IsweekAvgStat['isWeek'] == 0].sort_values(by='utilization', ascending=False).head(criteria)
        WeekMin = IsweekAvgStat[IsweekAvgStat['isWeek'] == 0].sort_values(by='utilization', ascending=True).head(criteria)
        WeekendMax = IsweekAvgStat[IsweekAvgStat['isWeek'] == 1].sort_values(by='utilization', ascending=False).head(criteria)
        WeekendMin = IsweekAvgStat[IsweekAvgStat['isWeek'] == 1].sort_values(by='utilization', ascending=True).head(criteria)

        NewCharger['wdMaxHour'] = str(WeekMax['hour'].values)
        NewCharger['wdMinHour'] = str(WeekMin['hour'].values)
        NewCharger['wkndMaxHour'] = str(WeekendMax['hour'].values)
        NewCharger['wkndMinHour'] = str(WeekendMin['hour'].values)

        #주중/주말 최대,최소 충전시간대
        NewCharger['wdMaxTz'] = comp.timezone_classification(WeekMax, 'max')
        NewCharger['wdMinTz'] = comp.timezone_classification(WeekMin, 'min')
        NewCharger['wkndMaxTz'] = comp.timezone_classification(WeekendMax, 'max')
        NewCharger['wkndMinTz'] = comp.timezone_classification(WeekendMin, 'min')

        #평균 통계값
        NewCharger['avgChargeTime'] = round(SelectCharger['chargingTime'].mean() / 60, 2)
        NewCharger['avgChargeCap'] = round(SelectCharger['charging_capacity'].mean(), 2)

        ChargerCheck.append(NewCharger)                                                 #신규 충전기 추가
        print("New charger is registered\n")


stations = pd.concat(ChargerCheck)
# 충전기 이용률 그룹화
stations.insert(9, 'wdrank', comp.utilization_group(stations['wdUtilization']))
stations.insert(11, 'wkndrank', comp.utilization_group(stations['wkndUtilization']))
stations.to_csv(DocPath + ChargerList, index=False, encoding='utf-8')
