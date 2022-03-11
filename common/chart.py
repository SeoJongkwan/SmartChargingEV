import seaborn as sns
from matplotlib import pyplot as plt

def value_count(df, col):
    df.value_counts(col).sort_values().plot(kind='barh')
    plt.title(col)
    plt.grid(True, axis='x')
    plt.tight_layout()
    plt.show()

