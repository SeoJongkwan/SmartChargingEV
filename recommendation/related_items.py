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
recommend_list = 'charger_recommendation.csv'

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

chargers = []
for n in range(len(exist_stations)):
# for n in range(1):
    station_name = exist_stations.iloc[n, 1]
    charger_id = int(exist_stations.iloc[n, 2])
    print(f"{n} station: {station_name} / charger id: {charger_id}")

    select_station = charger_history[(charger_history['station_name'] == station_name) & (charger_history['charger_code'] == charger_id)].reset_index(drop=True)
    charger = exist_stations.where((exist_stations['station_name'] == station_name) & (exist_stations['charger_id'] == charger_id)).dropna()
    charger = charger.astype({'charger_id': int})

    # 연관항목 초기화
    charger['chPlace'] = info.charger_place[0]
    charger['chOptm'] = info.charger_optime[0]
    charger['chTarget'] = info.charger_target[0]
    charger['distance'] = info.distance[0][0]
    charger['chDensity'] = info.charger_density[0][0]
    charger['numUsers'] = comp.num_users(select_station, 'station_name', 'charger_code')['user_cnt'].iloc[0].item()
    charger['chFee'] = info.charging_fee[0][0]
    charger['unableCh'] = info.unable_charge[0][0]

    chargers.append(charger)
    print("Related item data has been added.\n")

stations = pd.concat(chargers).sort_values(by=['station_name', 'charger_id'])
stations.insert(10, 'scoreAccess', comp.score_chplace(stations['chPlace']))
stations.insert(11, 'scoreNumUsers', comp.score_num_users(stations['numUsers']))

stations = stations.drop(['numUsers'], axis=1)
# 총점 계산 후, 정렬
stations['total'] = stations.iloc[:, 8:13].sum(axis=1)
stations['total'].sort_values(ascending=False)

# 추천 연관항목, 점수 저장
# evses.to_csv(doc_path + recommend_list, index=False, encoding='utf-8')

