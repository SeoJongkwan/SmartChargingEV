import datetime
import pandas as pd
import numpy as np
import plotly as py
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from common import info, chart
from extractor import mt

# dsr = mt.select('15')
# dsrACK = mt.select('1A')
# chart.value_count(dsr, 'Device Status')
# chart.value_count(dsrACK, 'Charger Number')
# dsr.columns
# dsrACK.columns
# chart.value_count(dsr, 'ChargerId')
# chart.value_count(dsrACK, 'charger_id')

# df = mt.select('all')
# chart.pie_chart(df, 'count', 'message_type')

# 기간 설정
df = mt.select_usage('charger_chargerusage')
start_date = datetime.date(2021, 9, 1)
df_duration = mt.select_time(df, 'start_time', start_date, 5)
# chart.pie_chart(df_duration, 'count', 'paying_method')

df_duration['is_member'] = np.where(df_duration['member_name']=='비회원', '비회원', '회원')
df1 = df_duration.groupby(['is_member', 'paying_method']).size().reset_index(name='count')
df_lst = list(df1.groupby('is_member'))

# here we want our grid to be 1 x 2
rows = 1
cols = 2
# continents are the first element in l
subplot_titles = [l[0] for l in df_lst]

# a compact and general version of what you did
specs = [[{'type': 'domain'}] * cols] * rows

# here the only difference from your code are the titles for subplots
fig = make_subplots(
    rows=rows,
    cols=cols,
    subplot_titles=subplot_titles,
    specs=specs,
    print_grid=True)

for i, l in enumerate(df_lst):
    # basic math to get col and row
    row = i // cols + 1
    col = i % (rows + 1) + 1
    # this is the dataframe for every continent
    d = l[1]
    fig.add_trace(
        go.Pie(labels=d["paying_method"],
               values=d["count"],
               showlegend=True,
               textposition='inside',
               textinfo='label+percent',
               hole=.3),
        row=row,
        col=col

    )

fig.update_layout(title="Paying Method by Member Type", title_x=0.5)
fig.show()