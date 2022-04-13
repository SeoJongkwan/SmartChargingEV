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
cs = usage_history[usage_history['station_name'] == charger_station]

InDeokWonIT_original = usage_history[usage_history["station_name"] == info.station_name[1]]
IT_col = ["charging_id", "station_name", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]
InDeokWonIT_original_col = InDeokWonIT_original[IT_col].reset_index(drop=True)

# 기간 설정
start_date = date(2021, 10, 1)
InDeokWonIT = mt.select_time(InDeokWonIT_original_col, 'start_time', start_date, 4)

# 시간정보 추가
component = component.base(InDeokWonIT)
InDeokWonIT = component.time_split('start_time')

ct_hour = []
for i in range(len(InDeokWonIT)):
    if InDeokWonIT['start_time'].dt.hour[i] != InDeokWonIT['end_time'].dt.hour[i]:
        ct_hour.append(InDeokWonIT.loc[i])

InDeokWonIT_hour = pd.DataFrame(ct_hour)
InDeokWonIT_hour['hour'] = InDeokWonIT_hour['end_time'].dt.hour

InDeokWonIT_dc_charger = pd.concat([InDeokWonIT, InDeokWonIT_hour]).sort_values('start_time').reset_index(drop=True)

InDeokWonIT_dc_charger['st_sec'] = 3600 - (InDeokWonIT_dc_charger['minute'] * 60)         #60분에서 충전 시작 분시간을 차감한 초시간
InDeokWonIT_dc_charger['ct_sec'] = (InDeokWonIT_dc_charger['end_time'] - InDeokWonIT_dc_charger['start_time']).dt.total_seconds()    #충전시간(초)
InDeokWonIT_dc_charger['ct_sec'] = InDeokWonIT_dc_charger['ct_sec'].astype(int)
InDeokWonIT_dc_charger['st_sec'] = InDeokWonIT_dc_charger['st_sec'].astype(int)

InDeokWonIT_dc_charger['ct_subtract'] = 0                            #충전 시작시간을 제외한 남은 시간 - 충전시간
InDeokWonIT_dc_charger['ct_next'] = 0                                #충전시간이 시작 분시간과 합하여 60분을 초과한 시간
InDeokWonIT_dc_charger['ct_seconds'] = 0                             #충전시간
InDeokWonIT_dc_charger['ct_subtract'] = InDeokWonIT_dc_charger['st_sec'] - InDeokWonIT_dc_charger['ct_sec']

for i in range(len(InDeokWonIT_dc_charger)):
    if InDeokWonIT_dc_charger['ct_subtract'][i] < 0:
        InDeokWonIT_dc_charger['ct_seconds'][i] = InDeokWonIT_dc_charger['st_sec'][i]
        InDeokWonIT_dc_charger['ct_next'][i + 1] = InDeokWonIT_dc_charger['ct_subtract'][i]
    else:
        InDeokWonIT_dc_charger['ct_seconds'][i] = InDeokWonIT_dc_charger['ct_sec'][i]

for i in range(len(InDeokWonIT_dc_charger)):
    if ((InDeokWonIT_dc_charger['ct_subtract'][i] < 0) & (InDeokWonIT_dc_charger['ct_next'][i] < 0)):
        InDeokWonIT_dc_charger['ct_seconds'][i] = abs(InDeokWonIT_dc_charger['ct_next'][i])

period = ["hour", "weekday", "day_of_week", "month"]
sel_period = period[0]

InDeokWonIT_group = InDeokWonIT_dc_charger.groupby(['month', sel_period]).size().reset_index(name='charging_cnt')

charging_cnt = list(InDeokWonIT_dc_charger.groupby(['month', sel_period]).size().to_numpy())
charging_amount = list(InDeokWonIT_dc_charger.groupby(['month', sel_period])['charging_capacity'].sum())
ct_seconds = list(InDeokWonIT_dc_charger.groupby(['month', sel_period])['ct_seconds'].mean())
InDeokWonIT_group['charging_amount'] = charging_amount
InDeokWonIT_group['ct_seconds'] = ct_seconds
occupation = InDeokWonIT_group['ct_seconds'].apply(lambda x: x / (24 * 60) * 100)
InDeokWonIT_group['occupation'] = occupation

InDeokWonIT_group['date'] = InDeokWonIT_group[['month', 'hour']].apply(lambda x: ' '.join(x.astype(str)), axis=1)

# 월별 이용률 비교
fig = px.bar(InDeokWonIT_group, x=sel_period, y='occupation', color='month', barmode='group', title=f"Utilization Rate per hours",
             color_discrete_sequence=[
                 px.colors.qualitative.Alphabet[15],
                 px.colors.qualitative.Plotly[2],
                 px.colors.qualitative.Plotly[9],
                 px.colors.qualitative.Alphabet[11]
                 ]
             )
fig.update_layout(xaxis= {"dtick":1})
fig.show()
