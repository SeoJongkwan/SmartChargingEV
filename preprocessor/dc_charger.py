from datetime import date
import pandas as pd
import numpy as np
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

haeorum_original = usage_history[usage_history["station_name"] == info.station_name[1]]
hae_col = ["charging_id","station_name","start_time","end_time","member_number","nonmember_number","member_name","charging_time","charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]
haeorum_original_col = haeorum_original[hae_col].reset_index(drop=True)

# 기간 설정
start_date = date(2021, 10, 1)
haeorum = mt.select_time(haeorum_original_col, 'start_time', start_date, 4)

# 시간정보 추가
componet_time = component.base(haeorum)
haeorum = componet_time.time_split('start_time')
haeorum.columns

different_hour = []
for i in range(len(haeorum)):
    if haeorum['start_time'].dt.hour[i] != haeorum['end_time'].dt.hour[i]:
        different_hour.append(haeorum.loc[i])

haeorum_new = pd.DataFrame(different_hour)
haeorum_new['hour'] = haeorum_new['end_time'].dt.hour

haeorum_expand = pd.concat([haeorum, haeorum_new]).sort_values('start_time').reset_index(drop=True)

haeorum_expand['st_sec'] = 3600 - (haeorum_expand['minute'] * 60)         #충전 시작시간의 분단위를 3600초(1시간)에서 차감한 초시간
haeorum_expand['ct_sec'] = (haeorum_expand['end_time'] - haeorum_expand['start_time']).dt.total_seconds()    #초단위 충전시간
haeorum_expand['ct_sec'] = haeorum_expand['ct_sec'].astype(int)
haeorum_expand['st_sec'] = haeorum_expand['st_sec'].astype(int)

haeorum_expand['ct_subtract'] = 0                            #충전 시작시간(초) - 충전 종료시간(초)
haeorum_expand['ct_next'] = 0                                #충전 시작시간의 분단위가 60분을 초과한 경우 남은 충전시간을 다음 시간으로 넘김
haeorum_expand['ct_seconds'] = 0                             #초단위 충전시간
haeorum_expand['ct_subtract'] = haeorum_expand['st_sec'] - haeorum_expand['ct_sec']

for i in range(len(haeorum_expand)):
    if haeorum_expand['ct_subtract'][i] < 0:
        haeorum_expand['ct_seconds'][i] = haeorum_expand['st_sec'][i]
        haeorum_expand['ct_next'][i + 1] = haeorum_expand['ct_subtract'][i]
    else:
        haeorum_expand['ct_seconds'][i] = haeorum_expand['ct_sec'][i]

for i in range(len(haeorum_expand)):
    if ((haeorum_expand['ct_subtract'][i] < 0) & (haeorum_expand['ct_next'][i] < 0)):
        haeorum_expand['ct_seconds'][i] = abs(haeorum_expand['ct_next'][i])

period = ["hour", "weekday", "day_of_week", "month"]
sel_period = period[0]


haeorum_group = haeorum_expand.groupby(['month', sel_period]).size().reset_index(name='charging_cnt')

charging_cnt = list(haeorum_expand.groupby(['month', sel_period]).size().to_numpy())
charging_amount = list(haeorum_expand.groupby(['month', sel_period])['charging_capacity'].sum())
ct_seconds = list(haeorum_expand.groupby(['month', sel_period])['ct_seconds'].mean())
haeorum_group['charging_amount'] = charging_amount
haeorum_group['ct_seconds'] = ct_seconds
occupation = haeorum_group['ct_seconds'].apply(lambda x: x / (24 * 60) * 100)
haeorum_group['occupation'] = occupation

# 월별 이용률 비교
fig = px.bar(haeorum_group, x=sel_period, y='occupation', color='month', barmode='group', title=f"Utilization Rate per hours",
             color_discrete_sequence=[
                 px.colors.qualitative.Alphabet[15],
                 px.colors.qualitative.Plotly[2],
                 px.colors.qualitative.Plotly[9],
                 px.colors.qualitative.Alphabet[11]
                 ]
             )
fig.update_layout(xaxis= {"dtick":1})
fig.show()
