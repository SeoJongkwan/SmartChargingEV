from datetime import date
import pandas as pd
import numpy as np
from common import info
from common import component
from extractor import mt

# usage_history = mt.select_usage('charger_chargerusage') # DB의 사용내역 데이터
# usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

filter_col = ["charging_id", "station_name", "charger_code", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]

doc_path = '../doc/'
charger_info = 'charger_list.csv'
charger_list = pd.read_csv(doc_path + charger_info)

# 사용내역 목록
usage_history_file = 'charger_usage_history.csv'
usage_history = pd.read_csv(doc_path + usage_history_file)
usage_history['start_time'] = pd.to_datetime(usage_history['start_time'], format='%Y-%m-%d %H:%M:%S')
usage_history['end_time'] = pd.to_datetime(usage_history['end_time'], format='%Y-%m-%d %H:%M:%S')
usage_history['charging_capacity'] = usage_history['charging_capacity'].apply(lambda x: x.replace(',', '')).astype('int64')
usage_history = usage_history[filter_col].reset_index(drop=True)

# timezone 선택
# usage_history['start_time'] = pd.to_datetime(usage_history['start_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')
# usage_history['end_time'] = pd.to_datetime(usage_history['end_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')

# 기간 설정
start_date = date(2022, 1, 1)
charger = mt.select_time(usage_history, 'start_time', start_date, 4)

# 시간정보 추가
comp = component.base(charger)
charger = comp.time_split('start_time')
charger['chargingTime'] =round((charger['end_time'] - charger['start_time']).dt.total_seconds(), 2)
charger['isWeek'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)
charger['charger_region'] = info.charger_region[0]
charger['charger_place'] = info.charger_place[0]
charger['wd_rank'] = 1
charger['wknd_rank'] = 1
charger['member_type'] = np.where(charger['member_name'] !='비회원', '회원', np.where(charger['roaming_card_entity'].notnull().values == True, '로밍회원', '비회원')) # 회원유형 구분
charger = charger[charger['charging_capacity'] > 0]           # 충전량 > 0
charger = charger.dropna(subset=['start_time', 'end_time'])

# 사용내역 충전소 목록
history_station = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')
history_station = history_station[['station_name', 'charger_code']].sort_values(by=['station_name']).reset_index(drop=True)

exist_stations = charger_list[charger_list['station_name'].isin(history_station['station_name'])].reset_index(drop=True)
print(f'New Stations corresponding DB: {len(exist_stations)}')

info_usage = []                                                           # 통계정보 저장 리스트

for n in range(len(exist_stations)):
    station_name = exist_stations.iloc[n, 1]
    charger_id = int(exist_stations.iloc[n, 2])
    print(f"{n} station: {station_name} / charger id: {charger_id}")
    usage_station = charger[(charger['station_name'] == station_name) & (charger['charger_code'] == charger_id)].reset_index(drop=True)
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

union_station = pd.concat(info_usage)
union_station.to_csv(doc_path + 'union_station.csv')