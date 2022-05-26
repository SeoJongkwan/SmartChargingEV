import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

doc_path = '../doc/'
df = pd.read_csv(doc_path + 'charger_list.csv', encoding='utf-8')
df = df[['station_name', 'charger_id','wdUtilization','wdRank', 'wkndUtilization', 'wkndRank']]
col = 'wdUtilization'
col1 =  'wkndUtilization'

minutes_by_utilization = {1: 20, 2: 40, 3: 60, 4: 90, 5: 200}

def check_util_outlier(data):
    q1, q3 = np.percentile(data, [25, 75])
    sns.boxplot(x=data, color='salmon')
    plt.title(f"Outlier Check based IQR({round(q3-q1,2)})")
    plt.show()

def utilization_group(data):
    check_util_outlier(data)
    util_division = []
    for n in data:
        if n <= 1.5:
            util_division.append(1)
        elif (n > 1.5) and (n <= 3.0):
            util_division.append(2)
        elif (n > 3.0) and (n <= 4.3):
            util_division.append(3)
        elif (n > 4.3) and ((n <= 6.0) | (n <= np.round(np.mean(data), 2))):
            util_division.append(4)
        else:
            util_division.append(5)
    return util_division

df['rank'] = utilization_group(df[col])
df['rank1'] = utilization_group(df[col1])

df = df[['station_name', 'charger_id','wdUtilization','wdRank', 'rank', 'wkndUtilization', 'wkndRank', 'rank1']]


