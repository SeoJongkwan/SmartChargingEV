from datetime import date
import pandas as pd
import numpy as np
from common import info
from common import component
from extractor import mt
import os.path
from openpyxl import Workbook

pd.set_option('mode.chained_assignment',  None)

# usage_history = mt.select_usage('charger_chargerusage')
# usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

# 충전소 선택
# charger_station = info.station_info[1]
# print(f"charger station: {charger_station}")

# charger_original = usage_history[usage_history["charger_num"] == charger_station[3]].reset_index(drop=True)
IT_col = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]
# charger_original_col = charger_original[IT_col].reset_index(drop=True)

# csv 데이터
filename = '../doc/charger30.csv'
data = pd.read_csv(filename)
data['start_time'] = pd.to_datetime(data['start_time'], format='%Y-%m-%d %H:%M:%S')
data['end_time'] = pd.to_datetime(data['end_time'], format='%Y-%m-%d %H:%M:%S')
data['charging_capacity'] = data['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')
charger_original_col = data[IT_col].reset_index(drop=True)

# 기간 설정
start_date = date(2022, 1, 1)
charger = mt.select_time(charger_original_col, 'start_time', start_date, 4)

# 시간정보 추가
component = component.base(charger)
charger = component.time_split('start_time')
charger['charging_time'] =round((charger['end_time'] - charger['start_time']).dt.total_seconds(), 2)
charger['is_weekend'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)

# 충전소 선택
stations = charger[['station_name', 'charger_code']].value_counts().index
n = 5 #n = 0 ~ 29
station_name = stations[n][0]
charger_code = stations[n][1]
select_station = charger[charger['station_name'] == station_name]
select_charger = select_station[select_station['charger_code']==charger_code]
print(f"station name: {station_name}")
print(f"charger code: {charger_code}")

charging_stat = component.get_weekdays_stat(select_charger)

charging_stat['charging_time'] = round(charging_stat['charging_time'] / 60, 2)                  #기간별 충전기 이용률
charging_info_per = component.get_charging_info_per(select_charger)                             #1회 충전시간, 충전량
week_occupation = charging_stat[charging_stat['is_weekend']==0]['occupation'].values[0]         #통계 데이터
weekend_occupation = charging_stat[charging_stat['is_weekend']==1]['occupation'].values[0]

load_station = mt.select_station(station_name, charger_code)                #DB에서 충전소 기본정보 SELECT
new_station = load_station[['station_id', 'station_name', 'address']]
new_station['charger_id'] = int(load_station['charger_id'][0].lstrip("0"))
new_station['place'] = info.charger_place[0]
new_station['operating_time'] = '24시간'
new_station['target'] = '전체'
new_station['1회 충전시간'] = charging_info_per['charging_time']
new_station['1회 충전량'] = charging_info_per['charging_capacity']


#주중/주말 판단
hour_charging_stat = component.get_week_hour_stat(select_charger)
week_max = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=False).head(5)
week_min = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=True).head(5)
weekend_max = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=False).head(5)
weekend_min = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=True).head(5)

new_station['week occupation'] = week_occupation
new_station['weekend occupation'] = weekend_occupation
new_station['week busy time'] = str(week_max['hour'].values)
new_station['week worst time'] = str(week_min['hour'].values)
new_station['weekend busy time'] = str(weekend_max['hour'].values)
new_station['weekend worst time'] = str(weekend_min['hour'].values)


station_path = '../doc/charger_list.xlsx'

if os.path.isfile(station_path):
    current_station_list = pd.read_excel(station_path)
    append_station_list = pd.concat([current_station_list, new_station])                #기존 충전소 목록에서 신규 충전소 추가
    append_station_list.duplicated(['station_name', 'charger_id'], keep='first')
    last_station = append_station_list.drop_duplicates()                                #기존 충전소 목록에서 신규 추가 충전소 중복제거
    last_station.to_excel(excel_writer=station_path, index=False)                       #최종 충전소 목록
    print(last_station[['station_name', 'charger_id']])
else :
    new_station.to_excel(excel_writer=station_path, index=False)
print("\nThe charger information has been entered.")

