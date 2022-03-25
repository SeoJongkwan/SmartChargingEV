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
cs = usage_history[usage_history['station_name'] == charger_station]

# 기간 설정
start_date = datetime.date(2021, 9, 1)
cs_date = mt.select_time(cs, 'start_time', start_date, 5)
# chart.pie_chart(df_duration, 'count', 'paying_method')

# 시간정보 추가
cs_date['month'] = cs_date['start_time'].dt.strftime('%Y-%m')
cs_date['hour'] = pd.DatetimeIndex(cs_date['start_time']).hour
cs_date['day_of_week'] = cs_date['start_time'].dt.day_name()

# 회원유형 구분
cs_date['member'] = np.where(cs['roaming_card_entity'] == 'KL(클린일렉스)', '회원', np.where(cs['roaming_card_entity'] == '', '비회원', '로밍회원'))

#
member_info = member.Plot(cs_date, 'member')

# 멤버별 충전횟수
member_info.show_charging_cnt('day_of_week')
# 멤버별 충전량 합계
member_info.show_charging_sum('day_of_week', 'charging_capacity')


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
# # chart.bar_sum(df, 'is_member', 'day_of_week', 'charging_capacity')