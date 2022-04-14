import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class Plot:
    def __init__(self, period):
        self.period = period

    def show_occupation(self, df, period, barmode):
        """
        :param period: day_of_week, hour
        :param barmode: group, stack
        :return: bar chart
        """
        fig = px.bar(df, x=df[period], y='occupation', color=df[period], barmode=barmode, title=f"Occupation per {period}")
        # fig.update_layout(xaxis= {"dtick":1})
        fig.update_layout(xaxis=dict(tickformat="%Y-%m"))
        fig.show()

    def show_charging_info(self, df, period, col):
        # lightsalmon(charging_count), gold(charging_amount)
        color = 'lightsalmon'
        fig = go.Figure(
            data=[
                go.Bar(name='Charging Time', x=df[period], y=df[col], yaxis='y', offsetgroup=2, marker={'color': 'cornflowerblue'}),
                go.Bar(name=f"{col}", x=df[period], y=df[col], yaxis='y2', offsetgroup=1, marker={'color': 'lightsalmon'})
            ],
            layout={
                'xaxis': {'title': f"{period}"},
                'yaxis': {'title': 'Charging Time (sec)'},
                'yaxis2': {'title': f"{col}", 'overlaying': 'y', 'side': 'right', 'showgrid': False}
            }
        )
        # fig.update_layout(xaxis= {"dtick":1})
        fig.show()




