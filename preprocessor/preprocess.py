import datetime
import pandas as pd
import numpy as np
from common import info, chart
from extractor import mt


dsr = mt.select('15')
dsrACK = mt.select('1A')
# chart.value_count(dsr, 'Device Status')
# chart.value_count(dsrACK, 'Charger Number')
# dsr.columns
# dsrACK.columns
# chart.value_count(dsr, 'ChargerId')
# chart.value_countunt(dsrACK, 'charger_id')

# 메시지 타입별 비율
# df = mt.select('all')
# chart.pie_chart(df, 'count', 'message_type')
