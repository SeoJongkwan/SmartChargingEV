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
        fig = px.bar(self.charger, x=period, y='occupation', color='month', barmode='group',
                     title=f"{title} - 시간대별 이용률",
                     color_discrete_sequence=[
                         px.colors.qualitative.Alphabet[15],
                         px.colors.qualitative.Plotly[2],
                         px.colors.qualitative.Plotly[9],
                         px.colors.qualitative.Alphabet[11]
                     ]
                     )
        fig.update_layout(xaxis={"dtick": 1})
        fig.show()