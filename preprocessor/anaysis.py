from datetime import date
import pandas as pd
import numpy as np
from common import info
from common import component
from chart import member
from chart import charger as charger_chart
from extractor import mt
import plotly.graph_objects as go
import plotly.express as px

usage_history = mt.select_usage('charger_chargerusage')
usage_history = usage_history[usage_history['end_time'] > usage_history['start_time']]

# 충전소 선택
charger_station = info.station_info[3]
print(f"charger station: {charger_station}")

charger_original = usage_history[usage_history["charger_num"] == charger_station[3][1]].reset_index(drop=True)
IT_col = ["charging_id", "station_name", "start_time", "end_time", "member_number", "nonmember_number", "member_name", "charging_time", "charging_capacity",
           "paid_fee","charging_fee","roaming_card_entity","charging_status"]
charger_original_col = charger_original[IT_col].reset_index(drop=True)

# timezone 선택
# cs['start_time'] = pd.to_datetime(cs['start_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')
# cs['end_time'] = pd.to_datetime(cs['end_time'],unit='ms', utc=True).dt.tz_convert('Asia/Seoul')

# 기간 설정
start_date = date(2021, 10, 1)
charger = mt.select_time(charger_original_col, 'start_time', start_date, 4)

# 시간정보 추가
component = component.base(charger)
charger = component.time_split('start_time')
charger['charging_time'] =round((charger['end_time'] - charger['start_time']).dt.total_seconds(), 2)

period = ["hour", "date", "weekday", "month"]
select_period = period[2]

if select_period == 'hour':
    charging_stat = component.get_hour_stat(charger)
elif select_period == 'date':
    charging_stat = component.get_day_stat(charger)
elif select_period == 'weekday' or period == 'dayofweek':
    charging_stat = component.get_week_stat(charger)
else:
    charging_stat = component.get_month_stat(charger)

#기간별 충전기 이용률
charging_stat['charging_time'] = round(charging_stat['charging_time'] / 60, 2)
charger_chart = charger_chart.Plot(charging_stat)
charger_chart.show_charger_occupation(select_period, charger_station[0])

# 이용률과 충전횟수
charger_chart.show_occupation_cnt(charging_stat, select_period, charger_station[0])

# 1회 충전시간, 충전량
charging_info_per = component.get_charging_info_per()
col = ["charging_cnt", "charging_capacity"]
select_col = col[1]
charger_chart.show_charging_info(select_period, select_col)


# # 회원유형 구분
# cs_date['member'] = np.where(cs_date['member_name'] !='비회원', '회원', np.where(cs_date['roaming_card_entity'] == '', '비회원', '로밍회원'))
#
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
# # 멤버별 충전량 합계
# member_info.show_charging_sum('hour', 'charging_capacity', 'stack')
# # 멤버별 충전횟수 scatter
# member_info.show_charging_cnt_scatter('hour')
# # 비중 차트
# member_info.show_info_ratio('paying_method')
# # 멤버별 비중차트
# member_info.show_info_ratio_group('paying_method')

