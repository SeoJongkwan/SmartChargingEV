import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

class Plot:
    def __init__(self, charger):
        self.charger = charger

    def show_charging_info(self, period, title, col1, col2):
        """
        :param period: weekday, hour, month
        :return: total pay & total energy => bar & line chart
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
                go.Bar(name=col1, x=self.charger[period], y=self.charger[col1], yaxis='y', offsetgroup=1, marker={'color': 'mediumaquamarine'}, text=self.charger[col1]),
                go.Scatter(name=col2, x=self.charger[period], y=self.charger[col2], yaxis='y2', line_shape='spline',
                           mode='lines+markers', marker={'color': 'gold'}, text=self.charger[col2])
            ],
            layout={
                'xaxis': {'title': f"{period}"},
                'yaxis': {'title': col1},
                'yaxis2': {'title': col2, 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        if period == 'month':
            fig.update_layout(xaxis=dict(tickformat="%Y-%m"), title=f"{title} - {title_period}별 " + col1 + " & " + col2)
        elif period == 'date':
            fig.update_layout(xaxis=dict(tickformat="%m-%d"), title=f"{title} - {title_period}별 " + col1 + " & " + col2)
        else:
            fig.update_layout(xaxis={"dtick": 1}, title=f"{title} - {title_period}별 " + col1 + " & " + col2)
        fig.update_traces(texttemplate='%{text:.2s}', textfont_size=20)
        fig.show()

    def single_chart(self, period, axis_name1, *args):
        fig = go.Figure(
            data=[
                go.Bar(name=args[0], x=self.charger[period], y=self.charger[args[0]], yaxis='y', offsetgroup=1,
                       marker={'color': 'mediumaquamarine'}, text=self.charger[args[0]])
            ],
            layout = {
                'yaxis': {'title': axis_name1},
            }
        )
        return fig

    def double_chart(self, period, axis_name1, axis_name2, *args):
        fig = go.Figure(
            data=[
                go.Bar(name=args[0], x=self.charger[period], y=self.charger[args[0]], yaxis='y', offsetgroup=1,
                       marker={'color': 'mediumaquamarine'}, text=self.charger[args[0]]),
                go.Scatter(name=args[1], x=self.charger[period], y=self.charger[args[1]], yaxis='y2', line_shape='spline',
                           mode='lines+markers', marker={'color': 'gold'}, text=self.charger[args[1]])
            ],
            layout={
                'yaxis': {'title': axis_name1},
                'yaxis2': {'title': axis_name2, 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        return fig

    def get_axis_name(self, col):
        if col == 'chTm2':
            axis_name = '충전시간(sec)'
        elif col == 'totEnergy':
            axis_name = '충전량(Wh)'
        elif col == 'totCost':
            axis_name = '충전요금(원)'
        elif col == 'userCnt':
            axis_name = '이용자 수(명)'
        else:
            axis_name = '이용률(%)'
        return axis_name

    def save_chart(self, target, filePath, duration, *args):
        period = self.charger.columns[0]
        if period == 'hour':
            title_period = '시간대'
            xaxis = {"dtick": 1}
            xaxis_range = [0, 23]
        elif period == 'date':
            title_period = '일'
            xaxis = dict(tickformat="%m-%d")
            xaxis_range = None
        elif period == 'weekday' or period =='dayofweek':
            title_period = '요일'
            xaxis = dict(
                        tickmode = 'array',
                        tickvals = [0, 1, 2, 3, 4, 5, 6],
                        ticktext = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    )
            xaxis_range = [0, 6]
        elif period == 'isWeek':
            title_period = '주중/주말'
            xaxis = dict(
                        tickmode = 'array',
                        tickvals = [0, 1],
                        ticktext = ['주중', '주말']
                    )
            xaxis_range = None
        elif period == 'month':
            title_period = '월'
            xaxis = dict(tickformat="%Y-%m")
            xaxis_range = None
        else:
            title_period = '충전소'
            xaxis = None
            xaxis_range = None

        target = target.replace('/', '_')

        if len(args) > 1:
            axis_name1 = self.get_axis_name(args[0])
            axis_name2 = self.get_axis_name(args[1])
            title = f"[{target}] ({duration}) {title_period}별 {axis_name1.split('(')[0]} & {axis_name2.split('(')[0]}"
            fig = self.double_chart(period, axis_name1, axis_name2, *args)
        else:
            axis_name1 = self.get_axis_name(args[0])
            title = f"[{target}] ({duration}) {title_period}별 {axis_name1.split('(')[0]}"
            fig = self.single_chart(period, axis_name1, *args)

        fig.update_layout(xaxis=xaxis, title=title, xaxis_range=xaxis_range, xaxis_title=title_period)
        fig.update_traces(texttemplate='%{text:.2s}', textfont_size=20)

        fileName = f"{filePath}/{title}.png"
        fig.write_image(fileName)