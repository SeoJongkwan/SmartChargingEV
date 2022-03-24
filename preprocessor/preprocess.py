import datetime
import pandas as pd
import numpy as np
import plotly as py
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from common import info, chart
from extractor import mt

station_name = info.station_name[3]

# dsr = mt.select('15')
# dsrACK = mt.select('1A')
# chart.value_count(dsr, 'Device Status')
# chart.value_count(dsrACK, 'Charger Number')
# dsr.columns
# dsrACK.columns
# chart.value_count(dsr, 'ChargerId')
# chart.value_count(dsrACK, 'charger_id')

# 메시지 타입별 비율
# df = mt.select('all')
# chart.pie_chart(df, 'count', 'message_type')

data = mt.select_usage('charger_chargerusage')

# 충전소 선택
df = data[data['station_name'] == station_name]

# 기간 설정
start_date = datetime.date(2021, 9, 1)
df_duration = mt.select_time(df, 'start_time', start_date, 5)
# chart.pie_chart(df_duration, 'count', 'paying_method')

df_duration['month'] = df_duration['start_time'].dt.strftime('%Y-%m')
df_duration['hour'] = pd.DatetimeIndex(df_duration['start_time']).hour

df_duration['day_of_week'] = df_duration['start_time'].dt.day_name()
df_duration['is_member'] = np.where(df['roaming_card_entity'] == 'KL(클린일렉스)', '회원', np.where(df['roaming_card_entity'] == '', '비회원', '로밍회원'))

# 멤버별 선호시간대 scatter
# chart.scatter_chart(df_duration, 'is_member', 'hour')

# 멤버별 선호시간대 누적 bar
chart.cumulative_bar_chart(df_duration, 'is_member', 'day_of_week')

# 멤버별 충전횟수
# chart.bar_cnt(df_duration, 'is_member', 'day_of_week')
# chart.bar_cnt(df_duration, 'is_member', 'hour')
# 충전소별 충전량 or 충전요금
# chart.bar_sum(df_duration, 'is_member', 'day_of_week', 'charging_capacity')

# 멤버별 지불방법 비율
# chart.double_pie_chart(df)

# 멤버별 충전횟수
# chart.bar_cnt(df, 'is_member', 'day_of_week')
# 멤버별 충전량 or 충전요금
# chart.bar_sum(df, 'is_member', 'day_of_week', 'charging_capacity')