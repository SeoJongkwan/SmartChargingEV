from datetime import date
import pandas as pd
import numpy as np
from common import info
from chart import member
from extractor import mt
import plotly.graph_objects as go

usage_history = mt.select_usage('charger_chargerusage')

# 충전소 선택
charger_station = info.station_name[0]
print(f"charger station: {charger_station}")
cs = usage_history[usage_history['station_name'] == charger_station]

# timezone 선택
# cs['start_time'] = pd.to_datetime(cs['start_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')
# cs['end_time'] = pd.to_datetime(cs['end_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')

# 기간 설정
start_date = date(2021, 10, 1)
cs_date = mt.select_time(cs, 'start_time', start_date, 4)

# 시간정보 추가
cs_date['month'] = cs_date['start_time'].dt.strftime('%Y-%m')
cs_date['hour'] = pd.DatetimeIndex(cs_date['start_time']).hour
cs_date['date'] = pd.DatetimeIndex(cs_date['start_time']).date
cs_date['day_of_week'] = cs_date['start_time'].dt.day_name()
cs_date['weekday'] = cs_date['start_time'].dt.weekday
cs_date['charging_time'] =(cs_date['end_time'] - cs_date['start_time']).dt.total_seconds()

import plotly.express as px
# df = cs_date.copy()
# period =  hour, weekday, month
period = 'hour'
df = cs_date.groupby([period, 'month']).size().reset_index(name='charging_count')
df2 = cs_date.groupby([period, 'month'])['charging_capacity'].sum().reset_index(name='charging_amount')
df3 = cs_date.groupby([period, 'month'])['charging_time'].sum().reset_index(name='charging_time')
df['utilization_rate'] = df3['charging_time'].apply(lambda x: x / (24 * 60 * 60 * 24) * 100)
df_merge = pd.concat([df, df2['charging_amount'], df3['charging_time']], axis=1, join='inner')

# 월별 이용률 비교
fig = px.bar(df, x=period, y='utilization_rate', color='month', barmode='group', title=f"Utilization Rate per hours",
             color_discrete_sequence=[
                 px.colors.qualitative.Alphabet[15],
                 px.colors.qualitative.Plotly[2],
                 px.colors.qualitative.Plotly[9],
                 px.colors.qualitative.Alphabet[11]
                 ]
             )
fig.update_layout(xaxis= {"dtick":1})
fig.show()

# charging_count, charging_amount
col = 'charging_amount'
# lightsalmon(charging_count), gold(charging_amount)
color = 'gold'
fig = go.Figure(
    data=[
        go.Bar(name='Charging Time', x=df_merge[period], y=df_merge["charging_time"], yaxis='y', offsetgroup=2, marker={'color': 'cornflowerblue'}),
        go.Bar(name=f"{col}", x=df_merge[period], y=df_merge[col], yaxis='y2', offsetgroup=1, marker={'color': color})
    ],
    layout={
        'xaxis': {'title' : f"{period}"},
        'yaxis': {'title': 'Charging Time (sec)'},
        'yaxis2': {'title': f"{col}", 'overlaying': 'y', 'side': 'right', 'showgrid' : False}
    }
)
fig.update_layout(xaxis= {"dtick":1})
fig.show()


# # 회원유형 구분
# cs_date['member'] = np.where(cs_date['member_name'] !='비회원', '회원', np.where(cs_date['roaming_card_entity'] == '', '비회원', '로밍회원'))

# # 회원유형 선택
# member_type = info.member_type[0] # 0: 회원, 1: 로밍회원, 2:비회원
# print(f"member type: {member_type}")
# cs_member_type = cs_date[cs_date['member'] == member_type]
#
# # 회원유형별 list
# if member_type == '회원':
#     members = cs_date[cs_date['member'] == member_type]['member_name'].value_counts().index
#
# elif member_type == '로밍회원':
#     members = cs_date[cs_date['member'] == member_type]['roaming_card_number'].value_counts().index
#
# else: # 비회원은 nonmember_number가 모두 상이하여 구분 어려움
#     members = cs_date[cs_date['member'] == member_type]['nonmember_number'].value_counts().index
#
# # 충전기이용 상위 회원 선택
# select_member = members[0]
# print(f"member: {select_member}")
# cs_member = cs_date[cs_date['member_name'] == select_member]
#
# # 전체: cs_date, 선택된 회원유형: cs_member_type, 선택된 회원: cs_member
# select_df = cs_date
# member_info = member.Plot(select_df, 'member')
#
# # 선택한 컬럼에 대한 비중
# select_col = 'paying_method'
# member_info.show_info_ratio(select_col)
#
# # 충전 소요시간 구하기
# charging_time = member_info.show_charging_time(select_df)
# print(f"충전 소요시간: \n{charging_time}")
#
# # 멤버별 충전횟수
# member_info.show_charging_cnt('month', 'stack')
# 멤버별 충전량 합계
# member_info.show_charging_sum('hour', 'charging_capacity', 'stack')
# 멤버별 충전횟수 scatter
# member_info.show_charging_cnt_scatter('hour')
# 비중 차트
# member_info.show_info_ratio('paying_method')
# 멤버별 비중차트
# member_info.show_info_ratio_group('paying_method')

