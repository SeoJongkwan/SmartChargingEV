import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class Plot:
    def __init__(self, charger):
        self.charger = charger

    def show_util_cap(self, df, period, title):
        """
        :param period: weekday, hour, month
        :return: utilization, charging capacity => line & bar chart
        """
        if period == 'hour':
            title_period = '시간대'
        elif period == 'date':
            title_period = '일'
        elif period == 'weekday' or period =='dayofweek':
            title_period = '요일'
        elif period == 'isWeek':
            title_period = '주중/주말'
        else:
            title_period = '월'

        fig = go.Figure(
            data=[
                go.Bar(name='Charging Capacity', x=df[period], y=df['charging_capacity'], yaxis='y',
                       marker={'color': 'lightblue'}, text=df['charging_capacity']),
                go.Scatter(name='Utilization', x=df[period], y=df['utilization'], yaxis='y2', line_shape='spline', mode='lines+markers',
                           marker={'color': 'cornflowerblue'}, text=df['utilization'])
            ],
            layout={
                'xaxis': {'title': f"{period}"},
                'yaxis': {'title': 'Charging Capacity'},
                'yaxis2': {'title': 'Utilization (%)', 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        if period == 'month':
            fig.update_layout(xaxis=dict(tickformat="%Y-%m"), title=f"{title} - {title_period}별 이용률 & 충전량") #yaxis_range=[0,50]
        elif period =='hour':
            fig.update_layout(xaxis={"dtick": 1}, xaxis_range=[0,23], title=f"{title} - {title_period}별 이용률 & 충전량")
        else:
            fig.update_layout(xaxis={"dtick": 1}, title=f"{title} - {title_period}별 이용률 & 충전량")
        fig.update_traces(texttemplate='%{text:.2s}', textfont_size=20)
        fig.show()

    def show_rank_info(self, df, title):
        fig = go.Figure(
            data=[
                go.Bar(name='Charging Capacity', x=df['month'], y=df['charging_capacity'], yaxis='y',
                       marker={'color': 'lightblue'}, text=df['charging_capacity']),
                go.Scatter(name='Num of users', x=df['month'], y=df['user_cnt'], yaxis='y2', line_shape='spline',
                           mode='lines+markers', marker={'color': 'mediumpurple'}, text=df['user_cnt'])
            ],
            layout={
                'xaxis': {'title': 'month'},
                'yaxis': {'title': 'Charging Capacity'},
                'yaxis2': {'title': 'Num of users (명)', 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        fig.update_layout(xaxis=dict(tickformat="%Y-%m"), title=f"{title}그룹 - 월별 충전량 & 이용자 수")
        fig.update_traces(texttemplate='%{text:.2s}', textfont_size=20)
        fig.show()

    def show_region_info(self, df):
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[df.charger_region, df.charging_time, df.charging_capacity, df.utilization],
                       fill_color='lavender',
                       align='left'))
        ])
        fig.show()