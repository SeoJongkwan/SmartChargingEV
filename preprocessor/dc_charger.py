from datetime import date
import pandas as pd
from common import info
from chart import member
from extractor import mt
import plotly.graph_objects as go
import plotly.express as px
from common import chart
from common import component

pd.set_option('mode.chained_assignment',  None)

usage_history = mt.select_usage('charger_chargerusage')

# 충전소 선택
charger_station = info.station_name[0]
print(f"charger station: {charger_station}")
InDeokWonIT_original = usage_history[usage_history["station_name"] == charger_station]
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
# InDeokWonIT_dc_charger1 = InDeokWonIT_dc_charger[['date','charging_cnt', 'charging_amount', 'charging_time']]

period = ["hour", "weekday", "day_of_week", "month"]
select_period = period[0]

InDeokWonIT_group = InDeokWonIT_dc_charger.groupby(['month', select_period]).size().reset_index(name='charging_cnt')

charging_cnt = list(InDeokWonIT_dc_charger.groupby(['month', select_period]).size().to_numpy())
charging_amount = list(InDeokWonIT_dc_charger.groupby(['month', select_period])['charging_capacity'].sum())
charging_time = list(InDeokWonIT_dc_charger.groupby(['month', select_period])['charging_time'].mean())
InDeokWonIT_group['charging_amount'] = charging_amount
InDeokWonIT_group['charging_time'] = charging_time
occupation = InDeokWonIT_group['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100)
InDeokWonIT_group['occupation'] = occupation

InDeokWonIT_group['date'] = InDeokWonIT_group[['month', 'hour']].apply(lambda x: ' '.join(x.astype(str)), axis=1)

# 월별 이용률 비교
fig = px.bar(InDeokWonIT_group, x=select_period, y='occupation', color='month', barmode='group',
             title=f"{charger_station} - 시간대별 이용률",
             color_discrete_sequence=[
                 px.colors.qualitative.Alphabet[15],
                 px.colors.qualitative.Plotly[2],
                 px.colors.qualitative.Plotly[9],
                 px.colors.qualitative.Alphabet[11]
                 ]
             )
fig.update_layout(xaxis= {"dtick":1})
fig.show()
