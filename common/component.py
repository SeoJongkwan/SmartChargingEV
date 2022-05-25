from common import info
import pandas as pd

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
            if 'date' in args:
                df2 = round(df1.groupby(['isWeek', 'hour']).mean().reset_index(), 1)
            else:
                df2 = round(df1.groupby([*args]).mean().reset_index(), 1)
        else:
            df2 = round(df1.groupby('isWeek').mean().reset_index(), 1)
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

    def utilization_gp(self, df):
        wdCond = df['wdUtilization'].between(1, 20)
        wkndCond = df['wkndUtilization'].between(1, 20)
        wdRange = df[wdCond]['wdUtilization']
        wkndRange = df[wkndCond]['wkndUtilization']
        df['wdRank'] = pd.cut(wdRange, 5, labels=[1, 2, 3, 4, 5], right=False)
        df['wkndRank'] = pd.cut(wkndRange, 5, labels=[1, 2, 3, 4, 5], right=False)
        return df
