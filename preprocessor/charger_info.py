import pandas as pd
import numpy as np
from datetime import date
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
ChargerHistory = mt.select_time(FilterCharger, 'start_time', StartDate, 3)
charger = ChargerHistory[ChargerHistory['charging_capacity'] > 0]           # 충전량 > 0
charger = charger.dropna(subset=['start_time', 'end_time'])
print(f'Registered Usage History: {len(UsageHistory)} (Capacity>0): {len(charger)}')

# 충전시간(seconds), 주중/주말 구분
comp = component.base(charger)
charger = comp.time_split('start_time')
charger['charging_time'] = (charger['end_time'] - charger['start_time']).dt.total_seconds()
charger = charger.astype({'charging_time': int})
charger['is_week'] = charger['weekday'].apply(lambda x: 1 if x > 4 else 0)
charger['memberType'] = np.where(charger['member_name'] != '비회원', '회원', np.where(charger['roaming_card_entity'].notnull().values == True, '로밍회원', '비회원')) # 회원유형 구분

# 신규 충전소 목록
NewStations = charger.drop_duplicates(['station_name', 'charger_code'], keep='first')
NewStations = NewStations[['station_name', 'charger_code']].sort_values(by=['station_name', 'charger_code']).reset_index(drop=True)

ExistStations = RegStations[RegStations['station_name'].isin(NewStations['station_name'])].reset_index(drop=True)
print(f'New Stations corresponding DB: {len(ExistStations)}')

ChargerCheck = []                                                           #신규츙전소 저장 리스트
# n = 2
for n in range(len(ExistStations)):
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

        ChargerCheck.append(NewCharger)                                                 #신규 충전기 추가
        print("New charger is registered\n")

stations = pd.concat(ChargerCheck).sort_values(by=['station_name', 'charger_id'])
# 충전기 요일 이용률 그룹 추가
# for n in range(0, 7):
#     stations.insert(n+9, info.weekday[n][1]+'Rank', comp.utilization_group(stations[info.weekday[n][1] + 'Utilization']))
stations.to_csv(DocPath + ChargerList, index=False, encoding='utf-8')
