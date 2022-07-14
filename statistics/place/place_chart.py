import pandas as pd
from datetime import date
from common import component, info
from extractor import mt
from chart import charger as charger_chart
pd.set_option('mode.chained_assignment',  None)

# 사용이력 DB
history = mt.select_usage(info.table[2])

# 사용내역 목록
history['chStartTm'] = pd.to_datetime(history['chStartTm'], format='%Y-%m-%d %H:%M:%S')
history['chEndTm'] = pd.to_datetime(history['chEndTm'], format='%Y-%m-%d %H:%M:%S')

filterCol = ["chId", "placeName", "evseId", "evseName", "chStartTm", "chEndTm", "memberNo", "nonMemberNo",
             "userName", "chTm2", "totEnergy", "payCost", "totCost", "rmCardEntity", "stoppedReason"]
history = history[filterCol].reset_index(drop=True)

startDate = date(2022, 4, 1)
numOfMonths = 3
chargerHistory = mt.select_time(history, 'chStartTm', startDate, numOfMonths)
chargerHistory = chargerHistory[chargerHistory['totEnergy'] > 0]           # 충전량 > 0
chargerHistory = chargerHistory.dropna(subset=['chStartTm', 'chEndTm'])

# 기간, 회원타입 컬럼 추가
comp = component.base(chargerHistory)
chargerHistory = comp.add_columns()

placeName = '전체 충전소'
placePath = comp.exist_path(placeName)

# 기간
startDateStr = str(pd.to_datetime(startDate, format='%Y-%m-%d')).split()[0].split('-', 1)[1]
duration = f"{startDateStr}, {str(numOfMonths)}"

# 합계 : 충전시간, 충전량, 충전요금, 사용자 수
dailySumStat = comp.charger_sum_stat(chargerHistory, 'date')
monthlySumStat = comp.charger_sum_stat(chargerHistory, 'month')
monthlyNumUsers = comp.num_users(chargerHistory, 'month')
monthlySumInfo = pd.merge(monthlySumStat, monthlyNumUsers, on=['month'], how='outer').fillna(0)

# 평균 충전시간, 충전량, 이용률
monthlyAvgStat = comp.charger_avg_stat(chargerHistory, 'month')
weekdayAvgStat = comp.charger_avg_stat(chargerHistory, 'weekday')
hourlyAvgStat = comp.charger_avg_stat(chargerHistory, 'hour')

# 월별 충전시간 & 이용자 수 합계
chargerChart = charger_chart.Plot(monthlySumInfo)
chargerChart.save_chart(placeName, placePath, duration, 'chTm2', 'userCnt')
# 월별 충전요금 & 충전량 합계
chargerChart.save_chart(placeName, placePath, duration, 'totCost', 'totEnergy')

# 일별 충전요금 & 충전량 합계
chargerChart = charger_chart.Plot(dailySumStat)
chargerChart.save_chart(placeName, placePath, duration, 'totCost', 'totEnergy')

# 충전소별 평균 이용률
placeAvgStat = comp.charger_avg_stat(chargerHistory, 'placeName')
chargerChart = charger_chart.Plot(placeAvgStat)
chargerChart.save_chart(placeName, placePath, duration, 'utz')