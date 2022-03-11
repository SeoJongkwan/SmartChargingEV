import pandas as pd
from common import info, chart
from extractor import mt


dsr = mt.select('15')
dsrACK = mt.select('1A')


chart.value_count(dsr, 'Device Status')
chart.value_count(dsrACK, 'Charger Number')

dsr.columns
dsrACK.columns
chart.value_count(dsr, 'ChargerId')
chart.value_count(dsrACK, 'charger_id')



