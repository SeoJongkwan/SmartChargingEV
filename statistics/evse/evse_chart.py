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

start_date = date(2022, 4, 1)
chargerHistory = mt.select_time(history, 'chStartTm', start_date, 3)
chargerHistory = chargerHistory[chargerHistory['totEnergy'] > 0]           # 충전량 > 0
chargerHistory = chargerHistory.dropna(subset=['chStartTm', 'chEndTm'])

# 기간, 회원타입 컬럼 추가
comp = component.base(chargerHistory)
chargerHistory = comp.add_columns()

# 충전기 목록
evses = chargerHistory.drop_duplicates(['placeName', 'evseId'], keep='first')
evses = evses[['placeName', 'evseId']].sort_values(by=['placeName', 'evseId']).reset_index(drop=True)

for n in range(len(evses)):
    placeName = evses.iloc[n, 0]
    evseId = int(evses.iloc[n, 1])
    print(f"{n} place: {placeName} / evse id: {evseId}")

    # 선택한 충전기 = 충전소이름 + 충전기코드(charger_id)
    selEvse = chargerHistory[(chargerHistory['placeName'] == placeName) & (chargerHistory['evseId'] == evseId)]

    # 합계 : 충전시간, 충전량, 충전요금, 사용자 수
    monthlySumStat = comp.charger_sum_stat(selEvse, 'month')
    monthlyNumUsers = comp.num_users(selEvse, 'month')
    monthlySumInfo = pd.merge(monthlySumStat, monthlyNumUsers, on=['month'], how='outer').fillna(0)

    # 평균 충전시간, 충전량, 이용률
    monthlyAvgStat = comp.charger_avg_stat(selEvse, 'month')
    weekdayAvgStat = comp.charger_avg_stat(selEvse, 'weekday')
    hourlyAvgStat = comp.charger_avg_stat(selEvse, 'hour')
    # 선택한 충전기, 충전기 경로
    target = placeName + '/' + str(evseId)
    evsePath = comp.exist_path(placeName, evseId)
    # 월별 충전시간 & 이용자 수 합계
    chargerChart = charger_chart.Plot(monthlySumInfo)
    chargerChart.save_chart(target, evsePath, 'chTm2', 'userCnt')
    # 월별 평균 충전량 & 이용률
    chargerChart = charger_chart.Plot(monthlyAvgStat)
    chargerChart.save_chart(target, evsePath, 'totEnergy', 'utz')
    # 월별 평균 이용률
    chargerChart = charger_chart.Plot(monthlyAvgStat)
    chargerChart.save_chart(target, evsePath, 'utz')
    # 요일별 평균 이용률
    chargerChart = charger_chart.Plot(weekdayAvgStat)
    chargerChart.save_chart(target, evsePath, 'utz')
    # 시간별 평균 이용률
    chargerChart = charger_chart.Plot(hourlyAvgStat)
    chargerChart.save_chart(target, evsePath, 'utz')
