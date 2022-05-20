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

IT_col = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]

# csv 파일에서 충전기 사용내역 데이터 load
filename = '../doc/charger_usage_history.csv'

data = pd.read_csv(filename)
data['start_time'] = pd.to_datetime(data['start_time'], format='%Y-%m-%d %H:%M:%S')
data['end_time'] = pd.to_datetime(data['end_time'], format='%Y-%m-%d %H:%M:%S')
data['charging_capacity'] = data['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')
charger_original_col = data[IT_col].reset_index(drop=True)

# 기간 설정
start_date = date(2022, 1, 1)
charger = mt.select_time(charger_original_col, 'start_time', start_date, 4)
charger = charger[charger['charging_capacity'] > 0] # 충전량 > 0

# 회원유형 구분
charger['member'] = np.where(charger['member_name'] !='비회원', '회원', np.where(charger['roaming_card_entity'].notnull().values == True, '로밍회원', '비회원'))

# 시간정보 추가
component = component.base(charger)
charger = component.time_split('start_time')
charger['charging_time'] = round((charger['end_time'] - charger['start_time']).dt.total_seconds(), 2)
charger['is_weekend'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)

# 충전소 선택
stations = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')          #충전소이름, 충전기코드 항목 추출
stations = stations[['station_name', 'charger_code']].reset_index(drop=True)

station_cnt = [*range(0,47)]
for n in station_cnt:
    station_name = stations.iloc[n, 0]
    charger_code = stations.iloc[n, 1]
    print(f"station name / charger code: {station_name, charger_code}")
    select_station = charger[charger['station_name'] == station_name]
    select_charger = select_station[select_station['charger_code']==charger_code]

    charging_stat = component.get_weekdays_stat(select_charger)

    charging_stat['charging_time'] = round(charging_stat['charging_time'] / 60, 2)                  #기간별 충전기 이용률
    charging_info_per = component.get_charging_info_per(select_charger)

    load_station = mt.select_station(station_name, charger_code)

    if load_station is None:
        pass
    else:
        new_station = load_station[['station_id', 'station_name', 'address']]           #station_type 제거
        new_station.rename(columns = {'station_id': 'stationId', 'station_name':'stationName'}, inplace=True)
        # new_station['stationType'] = int(new_station['stationType'][0].lstrip("0"))
        new_station['chargerId'] = int(load_station['charger_id'][0].lstrip("0"))
        new_station['chargerType'] = info.charger_type[1]
        new_station['chargePlace'] = info.charger_place[0]
        new_station['operatingTime'] = 24
        new_station['targetUser'] = 'all'
        new_station['onceChargeTime'] = round(charging_info_per['charging_time'], 0)
        new_station['onceChargeAmount'] = round(charging_info_per['charging_capacity'], 0)

        #주중/주말 판단
        hour_charging_stat = component.get_week_hour_stat(select_charger)
        criteria = 5
        week_max = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=False).head(criteria)
        week_min = hour_charging_stat[hour_charging_stat['is_weekend']==0].sort_values(by='occupation', ascending=True).head(criteria)
        weekend_max = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=False).head(criteria)
        weekend_min = hour_charging_stat[hour_charging_stat['is_weekend']==1].sort_values(by='occupation', ascending=True).head(criteria)

        member_charging_cnt = select_charger.groupby(['station_name', 'charger_code', 'member'])['member'].agg(['count']).reset_index() # 멤버별 충전횟수
        if len(member_charging_cnt[member_charging_cnt['member']=='로밍회원']) > 0  :
            new_station['roamingChargeCnt'] = member_charging_cnt[member_charging_cnt['member']=='로밍회원']['count'].iloc[0]
        elif len(member_charging_cnt[member_charging_cnt['member']=='회원']) > 0  :
            new_station['memberChargeCnt'] = member_charging_cnt[member_charging_cnt['member']=='회원']['count'].iloc[0]
        else :
            new_station['nonMemberChargeCnt'] = member_charging_cnt[member_charging_cnt['member'] == '비회원']['count'].iloc[0]

        week_type = charging_stat[['is_weekend', 'occupation']]
        if len(week_type) == 2:
            new_station['weekdayOccupation'] = week_type.iloc[0]['occupation']
            new_station['weekendOccupation'] = week_type.iloc[1]['occupation']
        elif len(week_type) == 1 and week_type.iloc[0]['is_weekend'] == 0:
            new_station['weekdayOccupation'] = week_type.iloc[0]['occupation']
        elif len(week_type) == 1 and week_type.iloc[0]['is_weekend'] == 1:
            new_station['weekendOccupation'] = week_type.iloc[0]['occupation']
        else:
            pass

        new_station['weekdayMajorHour'] = str(week_max['hour'].values)
        new_station['weekdayMinorHour'] = str(week_min['hour'].values)
        new_station['weekendMajorHour'] = str(weekend_max['hour'].values)
        new_station['weekendMinorHour'] = str(weekend_min['hour'].values)

        station_path = '../doc/charger_list.xlsx'

        if os.path.isfile(station_path):
            current_station_list = pd.read_excel(station_path)
            append_station_list = pd.concat([current_station_list, new_station]).reset_index(drop=True)   # 기존 충전소 목록에서 신규 충전소 추가
            append_station_list.duplicated(['stationName', 'chargerId'], keep='first')
            last_station = append_station_list.drop_duplicates(['stationName', 'chargerId']).reset_index(drop=True)  # 기존 충전소 목록에서 신규 추가 충전소 중복제거
            last_station.to_excel(excel_writer=station_path, index=False)  # 최종 충전소 목록
        else:
            new_station.to_excel(excel_writer=station_path, index=False)
        print("\nThe charger information has been entered.")