import datetime
import pandas as pd
import numpy as np
from common import info
from chart import member
from extractor import mt

usage_history = mt.select_usage('charger_chargerusage')

# 충전소 선택
charger_station = info.station_name[0]
print(f"charger station: {charger_station}")
df = usage_history[usage_history['station_name'] == charger_station]

cs = df.copy()
cs['start_time'] = pd.to_datetime(cs['start_time'], format='%Y-%m-%d %H:%M:%S')
cs['end_time'] = pd.to_datetime(cs['end_time'], format='%Y-%m-%d %H:%M:%S')

# 기간 설정
start_date = datetime.date(2021, 11, 1)
cs_date = mt.select_time(cs, 'start_time', start_date, 4)
# chart.pie_chart(df_duration, 'count', 'paying_method')

# 시간정보 추가
cs_date['month'] = cs_date['start_time'].dt.strftime('%Y-%m')
cs_date['hour'] = pd.DatetimeIndex(cs_date['start_time']).hour
cs_date['day_of_week'] = cs_date['start_time'].dt.day_name()
cs_date['charging_time'] = cs_date['end_time'] - cs_date['start_time']

# 회원유형 구분
cs_date['member'] = np.where(cs_date['member_name'] !='비회원', '회원', np.where(cs_date['roaming_card_entity'] == '', '비회원', '로밍회원'))
member_type = info.member_type[0] # 0: 회원, 1: 로밍회원, 2:비회원

# 회원 선택
if member_type == '회원':
    members = cs_date[cs_date['member'] == member_type]['member_name'].unique()

elif member_type == '로밍회원':
    members = cs_date[cs_date['member'] == member_type]['roaming_card_number'].unique()

else: # 비회원은 id가 모두 상이하여 구분 어려움
    members = cs_date[cs_date['member'] == member_type]['nonmember_number'].unique()

# 회원 선택
select_member = members[0]
cs_member = cs_date[cs_date['member_name'] == select_member]

#
member_info = member.Plot(cs_date, 'member')
# member_info = member.Plot(cs_member, 'member')

# 충전 소요시간 구하기
charging = cs_date['charging_time'].describe()
charging_time = member_info.show_charging_time(cs_date)
print(charging)

# 멤버별 충전횟수
member_info.show_charging_cnt('hour', 'stack')
# 멤버별 충전량 합계
member_info.show_charging_sum('hour', 'charging_capacity', 'stack')
# 멤버별 충전횟수 scatter
member_info.show_charging_cnt_scatter('hour')
# 비중 차트
member_info.show_info_ratio('paying_method')
# 멤버별 비중차트
# member_info.show_info_ratio_group('paying_method')


# # 멤버별 선호시간대 scatter
# # chart.scatter_chart(df_duration, 'is_member', 'hour')
#
# # 멤버별 선호시간대 누적 bar
# # chart.cumulative_bar_chart(df_duration, 'is_member', 'day_of_week')
#
# # 멤버별 충전횟수
# # chart.bar_cnt(df_duration, 'is_member', 'day_of_week')
# # chart.bar_cnt(df_duration, 'is_member', 'hour')
# # 충전소별 충전량 or 충전요금
# # chart.bar_sum(df_duration, 'is_member', 'day_of_week', 'charging_capacity')
#
# # 멤버별 지불방법 비율
# # chart.double_pie_chart(df)
#
# # 멤버별 충전횟수
# # chart.bar_cnt(df, 'is_member', 'day_of_week')
# # 멤버별 충전량 or 충전요금
# chart.bar_sum(df, 'is_member', 'day_of_week', 'charging_capacity')