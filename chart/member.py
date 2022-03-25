import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class Plot:
    def __init__(self, cs, member_type):
        self.cs = cs
        self.member_type = member_type

    def show_charging_cnt(self, period):
        """
        :param period: day_of_week, hour
        :return: bar chart
        """
        df = self.cs.groupby([self.member_type, period]).size().reset_index(name='cnt')
        fig = px.bar(df, x=period, y='cnt', color=self.member_type, barmode='group', title=f"Number of charges per {period}")
        fig.show()

    def show_charging_sum(self, period, col):
        """
        :param period: day_of_week, hour
        :param col: column name ex.charging_capacity
        :return: bar chart
        """
        df = self.cs.groupby([self.member_type, period])[col].sum().reset_index(name='sum')
        fig = px.bar(df, x=period, y='sum', color=self.member_type, barmode='group', title=f"Total {col} per {period}")
        fig.show()

