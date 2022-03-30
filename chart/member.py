import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class Plot:
    def __init__(self, cs, member_type):
        self.cs = cs
        self.member_type = member_type

    def show_charging_cnt(self, period, barmode):
        """
        :param period: day_of_week, hour
        :param barmode: group, stack
        :return: bar chart
        """
        df = self.cs.groupby([self.member_type, period]).size().reset_index(name='cnt')
        fig = px.bar(df, x=period, y='cnt', color=self.member_type, barmode=barmode, title=f"Number of charges per {period}")
        fig.show()

    def show_charging_sum(self, period, col, barmode):
        """
        :param period: day_of_week, hour
        :param col: column name ex.charging_capacity
        :param barmode: group, stack
        :return: bar chart
        """
        df = self.cs.groupby([self.member_type, period])[col].sum().reset_index(name='sum')
        fig = px.bar(df, x=period, y='sum', color=self.member_type, barmode=barmode, title=f"Total {col} per {period}")
        fig.show()

    def show_charging_cnt_scatter(self, period):
        """
        :param period: day_of_week, hour
        :return: scatter chart
        """
        df = self.cs.groupby([self.member_type, period]).size().reset_index(name='cnt')
        fig = px.scatter(df, x=period, y='cnt', color=self.member_type,  symbol=self.member_type, hover_data=['cnt'], title=f"Number of charges per {period}")
        fig.show()

    def show_info_ratio(self, col):
        """
        :param col: column name ex.paying_method
        :return: pie chart
        """
        df = self.cs.groupby([col]).size().reset_index(name='cnt')
        fig = px.pie(df, values='cnt', names=col, title=f"Percentage by {col}")
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont_size=30)
        # update_layout method used to modify change and size
        fig.update_layout(legend=dict(title_font_family="Times New Roman", font=dict(size=20)))
        fig.show()

    def show_info_ratio_group(self, col):
        """
        :param col: column name ex.paying_method
        :return: pie chart
        """
        df = self.cs.groupby([self.member_type, col]).size().reset_index(name='cnt')
        df_lst = list(df.groupby(self.member_type))
        # here we want our grid to be 1 x 2
        rows = 1
        cols = 3
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
            col = i % (rows + 2) + 1
            # this is the dataframe for every continent
            d = l[1]
            fig.add_trace(
                go.Pie(labels=d[col],
                       values=d["cnt"],
                       showlegend=True,
                       textposition='inside',
                       textinfo='label+percent',
                       textfont_size=30,
                       hole=.3),
                row=row,
                col=col
            )
        fig.update_layout(title="Paying Method by Member Type", title_x=0.5)
        fig.show()

    def show_charging_time(self, df):
        """
        :param df: dataframe name
        :return: dataframe
        """
        df['start_time'] < df['end_time']
        max = df['charging_time'].max()
        min = df['charging_time'].min()
        mean = df['charging_time'].mean()

        data = pd.DataFrame({"max": max, "min": min, "mean": mean}, index=['charging_time'])
        return data
