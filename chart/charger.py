import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

class Plot:
    def __init__(self, charger):
        self.charger = charger

    def show_charger_occupation(self, period, title):
        """
        :param period: time period
        :param title: station info
        :return: bar chart
        """
        if period == 'hour':
            title_period = '시간대'
        elif period == 'date':
            title_period = '일'
        elif period == 'weekday' or period =='dayofweek':
            title_period = '요일'
        else:
            title_period = '월'

        fig = px.bar(self.charger, x=period, y='occupation', barmode='group', text='occupation',
                     title=f"{title} - {title_period}별 이용률",
                     color_discrete_sequence=[
                         px.colors.qualitative.Alphabet[15],
                         px.colors.qualitative.Plotly[2],
                         px.colors.qualitative.Plotly[9],
                         px.colors.qualitative.Alphabet[11]
                     ]
                     )
        if period == 'month':
            fig.update_layout(xaxis=dict(tickformat="%Y-%m"))
        else:
            fig.update_layout(xaxis={"dtick": 1})
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', textfont_size=20)
        fig.show()

    def show_occupation_cnt(self, df, period, title):
        """
        :param period: weekday, hour, month
        :return: occupation, charging count => bar & line chart
        """
        if period == 'hour':
            title_period = '시간대'
        elif period == 'date':
            title_period = '일'
        elif period == 'weekday' or period =='dayofweek':
            title_period = '요일'
        else:
            title_period = '월'

        fig = go.Figure(
            data=[
                go.Bar(name='Occupation', x=df[period], y=df['occupation'], yaxis='y', offsetgroup=2,
                       marker={'color': 'skyblue'}, text=df['occupation']),

                go.Scatter(name='Charging Count', x=df[period], y=df['charging_cnt_mean'], yaxis='y2', marker={'color': 'gold'},
                       text=df['charging_cnt_mean'])
            ],
            layout={
                'xaxis': {'title': f"{period}"},
                'yaxis': {'title': 'Occupation (%)'},
                'yaxis2': {'title': 'Charging Count', 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        if period == 'month':
            fig.update_layout(xaxis=dict(tickformat="%Y-%m"), title=f"{title} - {title_period}별 이용률 & 충전횟수") #yaxis_range=[0,50]
        else:
            fig.update_layout(xaxis={"dtick": 1}, yaxis_range=[0,10], title=f"{title} - {title_period}별 이용률 & 충전횟수")
        fig.update_traces(texttemplate='%{text:.2s}', textfont_size=20)
        fig.show()

    def show_charging_info(self, period, col):
        """
        :param period: weekday, hour, month
        :return: charging time & charging count, charging time & charging capacity => bar chart
        """
        df = self.charger
        if col == 'charging_cnt':
            color = 'lightsalmon'
        else:
            color = 'gold'

        fig = go.Figure(
            data=[
                go.Bar(name='Charging Time', x=df[period], y=df['charging_time'], yaxis='y', offsetgroup=2, marker={'color': 'mediumpurple'}, text=df['charging_time']),
                go.Bar(name=f"{col}", x=df[period], y=df[col], yaxis='y2', offsetgroup=1, marker={'color': color}, text=df[col])
            ],
            layout={
                'xaxis': {'title': f"{period}"},
                'yaxis': {'title': 'Charging Time (hour)'},
                'yaxis2': {'title': f"{col}", 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        if period == 'month':
            fig.update_layout(xaxis=dict(tickformat="%Y-%m"))
        else:
            fig.update_layout(xaxis={"dtick": 1})
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside', textfont_size=20)
        fig.show()