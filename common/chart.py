import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from matplotlib import pyplot as plt

def value_count(df, col):
    """
    :param df: target
    :param col: specific column
    :return: bar chart
    """
    df.value_counts(col).sort_values().plot(kind='barh')
    plt.title(col)
    plt.grid(True, axis='x')
    plt.tight_layout()
    plt.show()

def pie_chart(df, col1, col2):
    df1 = df.groupby([col2]).size().reset_index(name='count')
    fig = px.pie(df1, values=col1, names=col2, title='percentage by '+col2)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.show()

def double_pie_chart(df):
    df1 = df.groupby(['is_member', 'paying_method']).size().reset_index(name='count')
    df = list(df1.groupby('is_member'))

    # here we want our grid to be 1 x 2
    rows = 1
    cols = 2
    # continents are the first element in l
    subplot_titles = [l[0] for l in df]

    # a compact and general version of what you did
    specs = [[{'type': 'domain'}] * cols] * rows

    # here the only difference from your code are the titles for subplots
    fig = make_subplots(
        rows=rows,
        cols=cols,
        subplot_titles=subplot_titles,
        specs=specs,
        print_grid=True)

    for i, l in enumerate(df):
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

def group_cnt(df, col, period):
    df1 = df.groupby([col, period]).size().reset_index(name='cnt')
    return df1

def group_sum(df, group, period, col):
    df1 = df.groupby([group, period])[col].sum().reset_index(name='sum')
    return df1

def bar_chart(df, x, y, colors, title):
    fig = px.bar(df, x=x, y=y, color=colors, barmode='group', title=title)
    fig.show()

def bar_cnt(df, group, period):
    df1 = group_cnt(df, group, period)
    bar_chart(df1, period, 'cnt', group, 'Number of charges per ' + period )

def bar_sum(df, group, period, col):
    df1 = group_sum(df, group, period, col)
    bar_chart(df1, period, 'sum', group, 'Total ' + col + ' per ' + period)

def scatter_chart(df, col, period):
    df1 = group_cnt(df, col, period)
    fig = px.scatter(df1, x=period, y="cnt", color=col, symbol=col, hover_data=['cnt'])
    fig.show()

def cumulative_bar_chart(df, col, period):
    df1 = group_cnt(df, col, period)
    fig = px.bar(df1, x=period, y="cnt", color=col, title="Charging day for each " + col)
    fig.show()
