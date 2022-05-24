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

    def chtime_by_hour(self, df):
        """
        :param df: a dataframe to calculate charging time
        :return: the dataframe with added charging time by hour
        """
        ct_hour = []
        for i in range(len(df)):
            if df['start_time'].dt.hour[i] != df['end_time'].dt.hour[i]:
                ct_hour.append(df.loc[i])

        station_hour = pd.DataFrame(ct_hour)
        station_hour['hour'] = station_hour['end_time'].dt.hour
        dc_charger = pd.concat([df, station_hour]).sort_values('start_time').reset_index(drop=True)

        dc_charger['st_sec'] = 3600 - (dc_charger['minute'] * 60)  # 충전 시작시간에서 가능한 충전시간
        dc_charger['ct_sec'] = (dc_charger['end_time'] - dc_charger['start_time']).dt.total_seconds()  # 충전시간
        dc_charger['ct_sec'] = dc_charger['ct_sec'].astype(int)
        dc_charger['st_sec'] = dc_charger['st_sec'].astype(int)
        dc_charger['ct_subtract'] = 0                           # 충전시간에서 충전 가능시간을 제외한 시간
        dc_charger['ct_next'] = 0                               # 충전시간에서 충전 시작시간의 가능 시간을 제외한 시간
        dc_charger['charging_time'] = 0                         # 충전시간
        dc_charger['ct_subtract'] = dc_charger['st_sec'] - dc_charger['ct_sec']

        for i in range(len(dc_charger)):
            if dc_charger['ct_subtract'][i] < 0:
                dc_charger['charging_time'][i] = dc_charger['st_sec'][i]
                dc_charger['ct_next'][i + 1] = dc_charger['ct_subtract'][i]
            else:
                dc_charger['charging_time'][i] = dc_charger['ct_sec'][i]
        for i in range(len(dc_charger)):
            if ((dc_charger['ct_subtract'][i] < 0) & (dc_charger['ct_next'][i] < 0)):
                dc_charger['charging_time'][i] = abs(dc_charger['ct_next'][i])
        return dc_charger

    def charger_avg_stat(self, df, *args):
        # df_grouped = df.groupby([*args])
        # # df1 = df_grouped.size().reset_index(name='chargingCnt')
        # df1 = df_grouped['chargingTime', 'charging_capacity'].apply(sum).reset_index()
        # df1['chargingTime'] = df['chargingTime'] / 60
        # df1['occupation'] = round(df1['chargingTime'].apply(lambda x: x / (24 * 60) * 100), 2)
        # df2 = round(df1.groupby('isWeek').mean(), 1)

        df_grouped = df.groupby([*args])
        df1 = df_grouped[['chargingTime', 'charging_capacity']].apply(sum).reset_index()
        df1['occupation'] = round(df1['chargingTime'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby('isWeek').mean().reset_index(), 1)
        return df2

    def timezone_condition(self, x):
        if x < 6:
            return info.dc_tz[0]
        elif x >= 6 and x < 12:
            return info.dc_tz[1]
        elif x >= 12 and x < 18:
            return info.dc_tz[2]
        else: return info.dc_tz[3]

    def timezone_classification(self, df, separator):
        if len(df) > 0 :
            df['timezone'] = df['hour'].apply(self.timezone_condition)
            timezone_sum = df.groupby('timezone')['occupation'].sum()
            timezone = timezone_sum.idxmax() if separator == 'max' else timezone_sum.idxmin()
        else : timezone = ''
        return timezone
