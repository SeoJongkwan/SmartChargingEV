from datetime import date
import pandas as pd
import numpy as np
from common import info
from common import component
from extractor import mt
import os.path
from openpyxl import Workbook
pd.set_option('mode.chained_assignment',  None)

# DB에서 충전기 사용내역 데이터 load
# usage_history = mt.select_usage('charger_chargerusage')
# usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

# 충전소 선택
# charger_station = info.station_info[1]
# print(f"charger station: {charger_station}")
# charger_original = usage_history[usage_history["charger_num"] == charger_station[3]].reset_index(drop=True)

# 등록된 충전소 목록
regStations = mt.all_stations()



#충전기 사용내역 데이터 csv load
chargerUsageHistory = '../doc/charger_usage_history.csv'

usageHistory = pd.read_csv(chargerUsageHistory)
usageHistory['start_time'] = pd.to_datetime(usageHistory['start_time'], format='%Y-%m-%d %H:%M:%S')
usageHistory['end_time'] = pd.to_datetime(usageHistory['end_time'], format='%Y-%m-%d %H:%M:%S')
usageHistory['charging_capacity'] = usageHistory['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')


filterColumn = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number",
                "member_name", "charging_time", "charging_capacity", "paid_fee","charging_fee","roaming_card_entity","charging_status"]
filterCharger = usageHistory[filterColumn].reset_index(drop=True)

# 기간 설정
startDate = date(2022, 1, 1)
charger = mt.select_time(filterCharger, 'start_time', startDate, 4)
charger = charger[charger['charging_capacity'] > 0] # 충전량 > 0

# 시간정보 추가
component = component.base(charger)
charger = component.time_split('start_time')
charger['chargingTime'] = round((charger['end_time'] - charger['start_time']).dt.total_seconds(), 2)
charger['isWeekend'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)

# 신규 충전소 목록
newStations = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')
newStations = newStations[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

exStations = regStations[regStations['station_name'].isin(newStations['station_name'])].reset_index(drop=True)
exStations = exStations.astype({'charger_id': int})


n = 0
#
# for n in range(len(exist_stations)):
stationName = exStations.iloc[n, 1]
chargerId = exStations.iloc[n, 2]
print(f"station: {stationName} / charger id: {chargerId}")
selectStation = charger[charger['station_name'] == stationName]
selectCharger = selectStation[charger['charger_code'] == chargerId].reset_index(drop=True)
selectCharger['paid_fee']= selectCharger['paid_fee'].apply(lambda x: x.replace(',', '')).astype('int')
selectCharger['charging_fee'] = selectCharger['charging_fee'].apply(lambda x: x.replace(',', '')).astype('int')

oneTimeStat = component.calc_one_time_stat(selectCharger)
newCharger = exStations.where((exStations['station_name'] == stationName) & (exStations['charger_id'] == chargerId)).dropna()

newCharger['chargerType'] = info.charger_type[1]
newCharger['chargePlace'] = info.charger_place[0]
newCharger['operatingTime'] = 24
newCharger['targetUser'] = 'all'
newCharger['onceChargeTime'] = round(oneTimeStat['chargingTime'], 0)
newCharger['onceChargeCap'] = round(oneTimeStat['charging_capacity'], 0)


monthly_charging_stat = component.calc_statistics(selectCharger, 'month')
weekday_charging_stat = component.calc_statistics(selectCharger, 'weekday')
daily_charging_stat = component.calc_statistics(selectCharger, 'date')
hourly_charging_stat = component.calc_statistics(selectCharger, 'hour')
isweek_charging_stat = component.calc_statistics(selectCharger, 'isWeekend', 'hour')


def get_week_hour_stat(df):
    df_grouped = df.groupby(['station_name', 'date', 'isWeekend', 'hour'])
    df2 = df_grouped.size().reset_index(name='charging_cnt')
    df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
    df2['chargingTime'] = list(df_grouped['chargingTime'].sum() /60)
    df2['occupation'] = round(df2['chargingTime'].apply(lambda x: x / (24 * 60) * 100), 2)

    charging_grouped = df2.groupby(['isWeekend', 'hour'])
    charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
    charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(), 1))
    charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
    charging_stat['chargingTime'] = list(charging_grouped['chargingTime'].mean())
    charging_stat['occupation'] = list(round(charging_grouped['occupation'].mean(), 1))
    return df2

def get_week_hour_stat1(df):
    df_grouped = df.groupby(['station_name', 'date', 'isWeekend', 'hour'])
    df2 = df_grouped.size().reset_index(name='charging_cnt')
    df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
    df2['chargingTime'] = list(df_grouped['chargingTime'].sum() / 60)
    df2['occupation'] = round(df2['chargingTime'].apply(lambda x: x / (24 * 60) * 100), 2)

    charging_grouped = df2.groupby(['isWeekend', 'hour'])
    charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
    charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(), 1))
    charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
    charging_stat['chargingTime'] = list(charging_grouped['chargingTime'].mean())
    charging_stat['occupation'] = list(round(charging_grouped['occupation'].mean(), 1))
    return charging_stat


isweek_charging_stat1 = get_week_hour_stat(selectCharger).sort_values(by=['hour'], ascending=True)
isweek_charging_stat2 = get_week_hour_stat1(selectCharger)


# criteria = 5
# weekMax = isweek_charging_stat[isweek_charging_stat['isWeekend'] == 0].sort_values(by='occupation', ascending=False).head(criteria)
# weekMin = isweek_charging_stat[isweek_charging_stat['isWeekend']==0].sort_values(by='occupation', ascending=True).head(criteria)
# weekendMax = isweek_charging_stat[isweek_charging_stat['isWeekend']==1].sort_values(by='occupation', ascending=False).head(criteria)
# weekendMin = isweek_charging_stat[isweek_charging_stat['isWeekend']==1].sort_values(by='occupation', ascending=True).head(criteria)
#
# newCharger['weekdayMajorHour'] = str(weekMax['hour'].values)
# newCharger['weekdayMinorHour'] = str(weekMin['hour'].values)
# newCharger['weekendMajorHour'] = str(weekendMax['hour'].values)
# newCharger['weekendMinorHour'] = str(weekendMin['hour'].values)

# one_time = component.calc_one_time_stat(isweek_charging_stat)
#
# weekType = one_time[['isWeekend', 'occupation']]
# if len(weekType) == 2:
#     newCharger['weekdayOccupation'] = weekType.iloc[0]['occupation']
#     newCharger['weekendOccupation'] = weekType.iloc[1]['occupation']
# elif len(weekType) == 1 and weekType.iloc[0]['is_weekend'] == 0:
#     newCharger['weekdayOccupation'] = weekType.iloc[0]['occupation']
# elif len(weekType) == 1 and weekType.iloc[0]['is_weekend'] == 1:
#     newCharger['weekendOccupation'] = weekType.iloc[0]['occupation']
# else:
#     print("No weekType")



station_path = '../doc/charger_list.xlsx'

if os.path.isfile(station_path):
    storedStations = pd.read_excel(station_path)
# addStation = pd.concat([storedStations, newCharger]).reset_index(drop=True)                          # 기존 충전소 목록에서 신규 충전소 추가
# addStation.duplicated(['station_name', 'charger_id'], keep='first')
# lastStation = addStation.drop_duplicates(['station_name', 'charger_id']).reset_index(drop=True)         # 기존 충전소 목록에서 신규 추가 충전소 중복제거
# lastStation.to_excel(excel_writer=station_path, index=False)  # 최종 충전소 목록
else:
    newCharger.to_excel(excel_writer=station_path, index=False)
    print("\nThe charger information has been entered.")