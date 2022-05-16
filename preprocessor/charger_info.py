from datetime import date
import pandas as pd
import numpy as np
from common import info
from common import component
from extractor import mt
import os.path
from openpyxl import Workbook

# usage_history = mt.select_usage('charger_chargerusage')
# usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

# 충전소 선택
# charger_station = info.station_info[1]
# print(f"charger station: {charger_station}")

# charger_original = usage_history[usage_history["charger_num"] == charger_station[3]].reset_index(drop=True)
IT_col = ["charging_id", "station_name", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
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

# 충전소 선택 (0~29)
stations = charger['station_name'].value_counts().index
select_station = stations[2]
select_charger = charger[charger['station_name'] == select_station]
print(f"station name: {select_station}")

charging_stat = component.get_weekdays_stat(select_charger)

#기간별 충전기 이용률
charging_stat['charging_time'] = round(charging_stat['charging_time'] / 60, 2)

# 1회 충전시간, 충전량
charging_info_per = component.get_charging_info_per(select_charger)

# 통계 데이터
week_occupation = charging_stat[charging_stat['is_weekend']==0]['occupation'].values[0]
weekend_occupation = charging_stat[charging_stat['is_weekend']==1]['occupation'].values[0]

hour_charging_stat = component.get_week_hour_stat(select_charger)
week_max = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=False).head(5)
week_min = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=True).head(5)
weekend_max = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=False).head(5)
weekend_min = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=True).head(5)

load_station = mt.select_station(select_station)
save_data = load_station[['station_id', 'station_name', 'address', 'charger_id']]
save_data['place'] = info.charger_place[0]
save_data['operating_time'] = '24시간'
save_data['target'] = '전체'
save_data['1회 충전시간'] = charging_info_per['charging_time']
save_data['1회 충전량'] = charging_info_per['charging_capacity']
save_data['week occupation'] = week_occupation
save_data['weekend occupation'] = weekend_occupation
save_data['week busy time'] = str(week_max['hour'].values)
save_data['week worst time'] = str(week_min['hour'].values)
save_data['wekkend busy time'] = str(weekend_max['hour'].values)
save_data['weekend worst time'] = str(weekend_min['hour'].values)

file = '../doc/charger_list.xlsx'

if os.path.isfile(file):
    load_data = pd.read_excel('../doc/charger_list.xlsx')
    append_data = load_data.append(save_data, 'sort=False')
    append_data.to_excel(excel_writer='../doc/charger_list.xlsx', index=False)
else :
    save_data.to_excel(excel_writer='../doc/charger_list.xlsx', index=False)

