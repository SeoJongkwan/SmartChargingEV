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

    def get_hour_stat(self, df):
        """
        :param df: a base dataframe
        :return: the dataframe with charging info by hour
        """
        df_grouped = df.groupby(['station_name', 'date', 'hour'])
        df2 = df_grouped.size().reset_index(name='charging_cnt')
        df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df2['charging_time'] = list(df_grouped['charging_time'].sum() / 60)
        df2['occupation'] = round(df2['charging_time'].apply(lambda x: x / (24 * 60) * 100), 2)

        charging_grouped = df2.groupby(['hour'])
        charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
        charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(), 1))
        charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
        charging_stat['charging_time'] = list(charging_grouped['charging_time'].mean())
        charging_stat['occupation'] = list(round(charging_grouped['occupation'].mean(), 2))
        return charging_stat



    def calc_statistics(self, df, *args):
        df_grouped = df.groupby(['station_name', *args])
        df1 = df_grouped.size().reset_index(name='charging_cnt')
        df1['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df1['chargingTime'] = list(df_grouped['chargingTime'].sum() /60)
        df1['occupation'] = round(df1['chargingTime'].apply(lambda x: x / (24 * 60) * 100), 2)
        return df1

    def calc_day_stat(self, df):
        df_grouped = df.groupby(['station_name', 'charger_code', 'month', 'date']).count().reset_index()
        # df1['charging_cnt'] = df_grouped['charging_id'].copy()
        # # df1['charging_cnt_mean'] = list(round(df1['charging_cnt'].mean(), 1))
        # df1['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        # df1['charging_time'] = list(df1['charging_time'].sum() / 60)
        # df1['occupation'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60) * 100), 2)
        return df_grouped

    def get_weekday_stat(self, df):
        df_grouped = df.groupby(['station_name', 'date', 'weekday'])
        df2 = df_grouped.size().reset_index(name='charging_cnt')
        df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df2['charging_time'] = list(df_grouped['charging_time'].sum() / 60)
        df2['occupation'] = round(df2['charging_time'] .apply(lambda x: x / (24 * 60) * 100), 2)

        charging_grouped = df2.groupby(['weekday'])
        charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
        charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(),1))
        charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
        charging_stat['charging_time'] = list(charging_grouped['charging_time'].mean())
        charging_stat['occupation'] = list(round(charging_grouped['occupation'].mean(), 2))
        return charging_stat




    def get_daily_stat(self, df):
        """
        :param df: a base dataframe
        :return: the dataframe with charging info by day
        """
        df_grouped = df.groupby(['station_name', 'is_weekend', 'date', 'weekday'])
        df2 = df_grouped.size().reset_index(name='charging_cnt')
        df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df2['charging_time'] = list(df_grouped['charging_time'].sum() / 60)
        df2['occupation'] = round(df2['charging_time'] .apply(lambda x: x / (24 * 60) * 100), 2)
        return df2

    def get_weekdays_stat(self, df):
        charging_grouped = df.groupby(['is_weekend'])
        df1 = charging_grouped.size().reset_index(name='charging_cnt')
        df1['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(),1))
        df1['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
        df1['charging_time'] = list(charging_grouped['charging_time'].mean())
        df1['occupation'] = list(round(charging_grouped['occupation'].mean(), 1))
        return df1

    def get_week_hour_stat(self, df):
        """
        :param df: a base dataframe
        :return: the dataframe with charging info by week, hour
        """
        df_grouped = df.groupby(['station_name','date', 'is_weekend', 'hour'])
        df2 = df_grouped.size().reset_index(name='charging_cnt')
        df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df2['charging_time'] = list(df_grouped['charging_time'].sum() / 60)
        df2['occupation'] = round(df2['charging_time'] .apply(lambda x: x / (24 * 60) * 100), 2)

        charging_grouped = df2.groupby(['is_weekend', 'hour'])
        charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
        charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(),1))
        charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
        charging_stat['charging_time'] = list(charging_grouped['charging_time'].mean())
        charging_stat['occupation'] = list(round(charging_grouped['occupation'].mean(), 1))
        return charging_stat

    def get_month_stat(self, df):
        """
        :param df: a base dataframe
        :return: the dataframe with charging info by month
        """
        df_grouped = df.groupby(['station_name', 'month', 'date'])
        df2 = df_grouped.size().reset_index(name='charging_cnt')
        df2['charging_capacity'] = list(df_grouped['charging_capacity'].sum())
        df2['charging_time'] = list(df_grouped['charging_time'].sum() / 60)
        df2['occupation'] = round(df2['charging_time'].apply(lambda x: x / (24 * 60) * 100), 2)

        charging_grouped = df2.groupby(['month'])
        charging_stat = charging_grouped.size().reset_index(name='charging_cnt')
        charging_stat['charging_cnt_mean'] = list(round(charging_grouped['charging_cnt'].mean(), 1))
        charging_stat['charging_capacity'] = list(charging_grouped['charging_capacity'].mean())
        charging_stat['charging_time'] = list(charging_grouped['charging_time'].mean())
        charging_stat['occupation'] = list(charging_grouped['occupation'].mean())
        return charging_stat

    def calc_one_time_stat(self, df):
        charging_stat = round(df[['charging_capacity']].mean(), 2)
        charging_stat['chargingTime'] = round(df['chargingTime'].mean() / 60, 2)
        return charging_stat