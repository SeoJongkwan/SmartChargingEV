import pandas as pd
import numpy as np
import os
from datetime import date
from common import info, component
from extractor import mt
from statistical_info import statistical_func, statistical_chart
import exception

doc_path = '../doc/'
charger_file = 'charger_list.csv'
# 추후, DB데이터 불러올 때 사용
# history_list = mt.select_usage('charger_chargerusage') # DB의 사용내역 데이터
# history_list = history_list[history_list['end_time'] > history_list['start_time']]
history_file = 'charger_usage_history.csv'
union_file = 'union_station.csv'    #충전소정보 + 충전이력

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

# timezone 선택
# history_list['start_time'] = pd.to_datetime(history_list['start_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')
# history_list['end_time'] = pd.to_datetime(history_list['end_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')

# 전처리 항목(2022년, 충전용량 0 초과, 충전 시작/종료 시간 null 체크)
start_date = date(2022, 1, 1)
charger_history = mt.select_time(history_list, 'start_time', start_date, 4)
charger_history = charger_history[charger_history['charging_capacity'] > 0]           # 충전량 > 0
charger_history = charger_history.dropna(subset=['start_time', 'end_time'])

# 충전시간, 주중/주말, 사용자타입 정보 추가
comp = component.base(charger_history)
charger_history = comp.time_split('start_time')
charger_history['charging_time'] = round((charger_history['end_time'] - charger_history['start_time']).dt.total_seconds(), 2)
charger_history['is_week'] = charger_history['weekday'].apply(lambda x: 1 if x > 4 else 0)
charger_history['member_type'] = np.where(charger_history['member_name'] != '비회원', '회원', np.where(charger_history['roaming_card_entity'].notnull().values == True, '로밍회원', '비회원')) # 회원유형 구분
# 지역, 장소, 이용률그룹 초기화
charger_history['charger_region'] = info.charger_region[0]
charger_history['charger_place'] = info.charger_place[0]
charger_history['wd_rank'] = 1
charger_history['wknd_rank'] = 1

# 사용내역 충전소 목록
history_station = charger_history.drop_duplicates(['station_name', 'charger_code'], keep='first')
history_station = history_station[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

# 사용내역과 통계정보에 속한 충전기
exist_stations = dc_chargers[dc_chargers['station_name'].isin(history_station['station_name'])].reset_index(drop=True)
print(f'New Stations corresponding DB: {len(exist_stations)}')

info_usage = []  # 통계정보 저장 리스트                                                          # 통계 통합정보 저장 리스트
# 사용내역에 통계정보에서 지역, 장소, 이용률그룹 값 변경
for n in range(len(exist_stations)):
    station_name = exist_stations.iloc[n, 1]
    charger_id = int(exist_stations.iloc[n, 2])
    print(f"{n} station: {station_name} / charger id: {charger_id}")
    usage_station = charger_history[(charger_history['station_name'] == station_name) & (charger_history['charger_code'] == charger_id)].reset_index(drop=True)
    info_station = exist_stations[(exist_stations['station_name'] == station_name) & (exist_stations['charger_id'] == charger_id)].reset_index(drop=True) #charger_code -> charger_id

    if usage_station.empty:
        print("There are Station but, no Charger ID\n")
    else:
        usage_station['charger_region'] = info_station['address'].str.split().str[0].item()
        usage_station['charger_place'] =  info_station['chargerPlace'].item()
        usage_station['wd_rank'] = info_station['wdrank'].item()
        usage_station['wknd_rank'] = info_station['wkndrank'].item()

        info_usage.append(usage_station)
        print("Charger info merged.\n")

# 통합정보 file 저장
union_station = pd.concat(info_usage)
union_station.to_csv(doc_path + union_file)

# 지역, 장소, 이용률그룹별 grouping
stat_func = statistical_func.base(union_station)
regional_stat = stat_func.variable_avg_stat(union_station, 'charger_region')
place_stat = stat_func.variable_avg_stat(union_station, 'charger_place', 'hour')

# 장소 시간대별 이용률
stat_chart = statistical_chart.Plot(place_stat)
select_place = info.charger_place[0]
place = place_stat[place_stat['charger_place']==select_place]
# stat_chart.show_util_cap(place, 'hour', select_place)

# 지역 충전시간, 충전량, 이용률
region = regional_stat.drop(columns='charger_code')
# region.rename(columns={'charger_region':'지역', 'charging_time':'충전시간', 'charging_capacity':'충전량', 'utilization':'이용률'}, inplace=True)
# stat_chart.show_region_info(region)

# 이용률그룹 충전량과 이용자 수
select_week = info.week_type[0][0]
select_col = 'wd_rank' if select_week == 0 else 'wknd_rank'
select_rank = 2
week_df = union_station[(union_station['is_week'] == select_week) & (union_station[select_col] == select_rank)]

if len(week_df) == 0:
    raise exception.FileExistException

util_stat = stat_func.variable_avg_stat(week_df, 'month')
num_users = stat_func.num_users(week_df, select_col)
merge_util = pd.merge(util_stat, num_users, on=['month'], how='inner')
title = info.week_type[select_week][1] + ' ' + str(select_rank)
stat_chart.show_rank_info(merge_util, title)

# 전체 충전소 기간별 차트 (월, 요일, 시간대, 주중/주말)
# monthly_avg_stat = stat_func.variable_avg_stat(union_station, 'month')
# weekday_avg_stat = stat_func.variable_avg_stat(union_station, 'weekday')
# hourly_avg_stat =  stat_func.variable_avg_stat(union_station, 'hour')
# isweek_avg_stat = stat_func.variable_avg_stat(union_station, 'is_week')
# charger_name = '전체 충전기'
# stat_chart.show_util_cap(monthly_avg_stat, 'month', charger_name)

# 개별 충전소 기간별 차트 (월, 요일, 시간대, 주중/주말, 주중/주말 시간대)
n=0 # 충전소 선택
station_name = exist_stations.iloc[n, 1]
charger_id = int(exist_stations.iloc[n, 2])
select_charger = union_station[(union_station['station_name'] == station_name) & (union_station['charger_code'] == charger_id)].reset_index(drop=True)

monthly_avg_stat = stat_func.variable_avg_stat(select_charger, 'month')
weekday_avg_stat = stat_func.variable_avg_stat(select_charger, 'weekday')
hourly_avg_stat =  stat_func.variable_avg_stat(select_charger, 'hour')
isweek_avg_stat = stat_func.variable_avg_stat(select_charger, 'is_week')
isweek_hour_stat = stat_func.variable_avg_stat(select_charger, 'is_week', 'hour')

# 충전기명 = 충전소명 + 충전기코드
charger_name = station_name + str(charger_id)
# stat_chart.show_util_cap(monthly_avg_stat, 'month', charger_name)