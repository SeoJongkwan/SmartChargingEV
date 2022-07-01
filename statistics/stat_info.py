import pandas as pd
import os
from datetime import date
from common import component, info
from extractor import mt
import exception
pd.set_option('mode.chained_assignment',  None)

doc_path = '../doc/'
charger_file = 'charger_list.csv'
history_file = 'charger_usage_history.csv'
charger_stat_list = 'charger_stat_list.csv'

if not os.path.isfile(doc_path + charger_file):
    raise exception.FileExistException
else:
    charger_list = pd.read_csv(doc_path + charger_file)
    history_list = pd.read_csv(doc_path + history_file)

# 급속 충전기 추출
dc_chargers = charger_list[charger_list['chargerType'] == info.charger_type[1]]
# 사용내역 목록
history_list['start_time'] = pd.to_datetime(history_list['start_time'], format='%Y-%m-%d %H:%M:%S')
history_list['end_time'] = pd.to_datetime(history_list['end_time'], format='%Y-%m-%d %H:%M:%S')
history_list['charging_capacity'] = history_list['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')

filter_col = ["charging_id", "station_name", "charger_code", "charger_name", "start_time", "end_time", "member_number",
              "nonmember_number", "member_name", "charging_time", "charging_capacity","paid_fee","charging_fee",
              "roaming_card_entity", "charging_status"]
history_list = history_list[filter_col].reset_index(drop=True)

start_date = date(2022, 1, 1)
charger_history = mt.select_time(history_list, 'start_time', start_date, 3)
charger_history = charger_history[charger_history['charging_capacity'] > 0]           # 충전량 > 0
charger_history = charger_history.dropna(subset=['start_time', 'end_time'])

# 기간, 회원타입 컬럼 추가
comp = component.base(charger_history)
charger_history = comp.add_columns()

# 사용내역 충전소 목록
history_station = charger_history.drop_duplicates(['station_name', 'charger_code'], keep='first')
history_station = history_station[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

# 사용내역과 통계정보에 속한 충전기
exist_stations = dc_chargers[dc_chargers['station_name'].isin(history_station['station_name'])].reset_index(drop=True).sort_values(by=['station_name', 'charger_id'])
print(f'New Stations corresponding DB: {len(exist_stations)}')

charger_stat = []

for n in range(len(exist_stations)):
# for n in range(1):
    station_name = exist_stations.iloc[n, 1]
    charger_id = int(exist_stations.iloc[n, 2])
    print(f"{n} station: {station_name} / charger id: {charger_id}")

    # 신규 충전기 = 충전소이름 + 충전기코드(charger_id)
    add_charger = exist_stations.where((exist_stations['station_name'] == station_name) & (exist_stations['charger_id'] == charger_id)).dropna()
    add_charger = add_charger.astype({'charger_id': int})

    select_station = charger_history[(charger_history['station_name'] == station_name) & (charger_history['charger_code'] == charger_id)].reset_index(drop=True)
    weekday_avg_stat = comp.charger_avg_stat(select_station, 'weekday')
    weekday_hour_stat = comp.charger_avg_stat(select_station, 'weekday', 'hour')
    isweek_avg_stat = comp.charger_avg_stat(select_station, 'is_week')

    # 일 평균 이용률
    add_charger['utilization'] = round(isweek_avg_stat['utilization'].mean(), 1)

    # 평균 통계값
    add_charger['avg_charge_time'] = round(select_station['charging_time'].mean() / 60, 2)
    add_charger['avg_charge_cap'] = round(select_station['charging_capacity'].mean(), 2)

    monDict = {}
    tueDict = {}
    wedDict = {}
    thuDict = {}
    friDict = {}
    satDict = {}
    sunDict = {}

    weekdays = weekday_avg_stat['weekday']
    for n in range(len(weekdays)):
        valList = []
        keyList = ['weekday', 'utilization', 'rank', 'dawnUtil', 'amUtil', 'pmUtil', 'nightUtil']

        weekday = weekday_avg_stat['weekday'][n] # 요일
        utilization = weekday_avg_stat['utilization'][n] # 요일 이용률
        rank = comp.utilization_group(utilization)[0] # 요일 이용률 그룹
        dawn_utilization = comp.tz_util(weekday_hour_stat, weekday, info.dc_tz[0]) # 새벽 이용률
        am_utilization = comp.tz_util(weekday_hour_stat, weekday, info.dc_tz[1]) # 오전 이용률
        pm_utilization = comp.tz_util(weekday_hour_stat, weekday, info.dc_tz[2]) # 오후 이용률
        night_utilization = comp.tz_util(weekday_hour_stat, weekday, info.dc_tz[3]) # 밤 이용률

        valList.append(weekday)
        valList.append(utilization)
        valList.append(rank)
        valList.append(dawn_utilization)
        valList.append(am_utilization)
        valList.append(pm_utilization)
        valList.append(night_utilization)

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

    add_charger['mon_util'] = str(monDict)
    add_charger['tue_util'] = str(tueDict)
    add_charger['wed_util'] = str(wedDict)
    add_charger['thu_util'] = str(thuDict)
    add_charger['fri_util'] = str(friDict)
    add_charger['sat_util'] = str(satDict)
    add_charger['sun_util'] = str(sunDict)

    charger_stat.append(add_charger)  # 충전기 통계정보 추가
    print("New charger is registered\n")

stations = pd.concat(charger_stat).sort_values(by=['station_name', 'charger_id'])
stations.to_csv(doc_path + charger_stat_list, index=False, encoding='utf-8')
