import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import info

class base:
    def __init__(self, df):
        self.df = df

    def time_split(self, column):
        """
        :param column: a column name indicating start time
        :return: a dataframe with (month, date, weekday, hour, minute) column
        """
        self.df['month'] = self.df[column].dt.strftime('%Y-%m')
        self.df['date'] = self.df[column].dt.date
        self.df['weekday'] = self.df[column].dt.weekday
        self.df['day_of_week'] = self.df[column].dt.day_name()
        self.df['hour'] = self.df[column].dt.hour
        self.df['minute'] = self.df[column].dt.minute
        return self.df

    def charger_avg_stat(self, df, *args):
        df_grouped = df.groupby([*args])
        df1 = df_grouped[['chargingTime', 'charging_capacity']].apply(sum).reset_index()
        df1['utilization'] = round(df1['chargingTime'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        if 'hour' in args:
            if 'isWeek' in args:
                df2 = round(df1.groupby(['isWeek', 'hour']).mean().reset_index(), 1)
            elif 'date' in args:
                df2 = round(df1.groupby(['hour']).mean().reset_index(), 1)
            else:
                df2 = round(df1.groupby([*args]).mean().reset_index(), 1)
        elif 'month' in args:
            df2 = round(df1.groupby('month').mean().reset_index(), 1)
        else:
            df2 = round(df1.groupby([*args]).mean().reset_index(), 1)
        return df2

    def timezone_condition(self, x):
        if x < 6:
            return info.dc_tz[0]
        elif (x >= 6) and (x < 12):
            return info.dc_tz[1]
        elif (x >= 12) and (x < 18):
            return info.dc_tz[2]
        else:
            return info.dc_tz[3]

    def timezone_classification(self, df, separator):
        if len(df) > 0:
            df['timezone'] = df['hour'].apply(self.timezone_condition)
            timezone_sum = df.groupby('timezone')['utilization'].sum()
            timezone = timezone_sum.idxmax() if separator == 'max' else timezone_sum.idxmin()
        else:
            timezone = ''
        return timezone


    def check_util_outlier(self, data):
        q1, q3 = np.percentile(data, [25, 75])
        sns.boxplot(x=data, color='salmon')
        plt.title(f"Outlier Check based IQR({round(q3-q1,2)})")
        plt.show()

    def utilization_group(self, data):
        self.check_util_outlier(data)
        util_division = []
        for n in data:
            if n <= 1.0:
                util_division.append(1)
            elif (n > 1.1) and (n <= 2.8):
                util_division.append(2)
            elif (n > 2.8) and (n <= 4.2):
                util_division.append(3)
            elif (n > 4.2) and (n <= 5.6):
                util_division.append(4)
            elif (n > 5.6) and ((n <= 6.9) | (n <= np.round(np.mean(data), 2))):
                util_division.append(5)
            else:
                util_division.append(6)
        return util_division

