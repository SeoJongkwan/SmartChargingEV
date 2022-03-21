import seaborn as sns
import plotly.express as px
from matplotlib import pyplot as plt

def value_count(df, col):
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

