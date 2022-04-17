from datetime import date
import pandas as pd
from extractor import mt
import plotly.graph_objects as go
import plotly.express as px

from common import info
from common import component
from chart import member
from chart import charger

pd.set_option('mode.chained_assignment',  None)

usage_history = mt.select_usage('charger_chargerusage')
usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

# 충전기선택: station name, station code, charger code, charger num
charger_station = info.station_info[3]
print(f"charger station: {charger_station}")
InDeokWonIT_original = usage_history[usage_history["charger_num"] == charger_station[3][1]].reset_index(drop=True)
IT_col = ["charging_id", "station_name", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]
InDeokWonIT_original_col = InDeokWonIT_original[IT_col].reset_index(drop=True)

# 기간 설정
start_date = date(2021, 10, 1)
InDeokWonIT = mt.select_time(InDeokWonIT_original_col, 'start_time', start_date, 4)

# 시간정보 추가
component = component.base(InDeokWonIT)
InDeokWonIT = component.time_split('start_time')
InDeokWonIT_dc_charger = component.chtime_by_hour(InDeokWonIT)

period = ["hour", "weekday", "date", "month"]
select_period = period[3]

InDeokWonIT_stat = component.get_charging_value(InDeokWonIT_dc_charger, select_period)

# InDeokWonIT_grouped = InDeokWonIT_dc_charger.groupby(['month', 'date', select_period])
# InDeokWonIT_stat = InDeokWonIT_grouped.size().reset_index(name='charging_cnt')
# InDeokWonIT_stat['charging_capacity'] = list(InDeokWonIT_grouped['charging_capacity'].sum())
# InDeokWonIT_stat['charging_time'] = list(InDeokWonIT_grouped['charging_time'].sum()/60)
# InDeokWonIT_stat['occupation'] = round(InDeokWonIT_stat['charging_time'].apply(lambda x: x / (24 * 60) * 100),2)
# InDeokWonIT_group['date'] = InDeokWonIT_group[['month', 'hour']].apply(lambda x: ' '.join(x.astype(str)), axis=1)

# charging_grouped = InDeokWonIT_stat.groupby(['month', select_period])
# charging_stat= charging_grouped.size().reset_index(name='charging_cnt')
# charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
# charging_stat['occupation'] = list(charging_grouped['occupation'].mean())

#시간대별 충전기 이용률
charger_chart = charger.Plot(InDeokWonIT_stat)
charger_chart.show_charger_occupation(select_period, charger_station[0])