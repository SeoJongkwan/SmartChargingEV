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
        self.df['is_week'] =  self.df['weekday'].apply(lambda x: 1 if x > 4 else 0)
        return self.df

    def add_columns(self):
        self.time_split('start_time')
        self.df['charging_time'] = (self.df['end_time'] - self.df['start_time']).dt.total_seconds()
        self.df = self.df.astype({'charging_time': int})
        self.df['member_type'] = np.where(self.df['member_name'] != '비회원', '회원',np.where(self.df['roaming_card_entity'].notnull().values == True, '로밍회원', '비회원'))  # 회원유형 구분
        return self.df

    def charger_avg_stat(self, df, *args):
        df_grouped = df.groupby([*args, 'date'])
        df1 = df_grouped[['charging_time', 'charging_capacity']].apply(sum).reset_index()
        df1['utilization'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby([*args]).mean().reset_index(), 1)

        if 'weekday' in args and 'hour' in args:
            df2 = self.set_weekday_hour(df2)
        return df2

    def set_weekday_hour(self, df):
        # 없는 시간대는 기본값 0
        weekday_list = list(range(0, 7))
        hour_list = list(range(0, 24))

        dfs = []
        for n in range(len(weekday_list)):
            df_wh = pd.DataFrame(hour_list, columns=['hour'])
            df_wh['weekday'] = n
            dfs.append(df_wh)

        df_sort = pd.concat(dfs).sort_values(by=['weekday']).reset_index(drop='index')
        df1 = pd.merge(df, df_sort, on=['weekday', 'hour'], how='outer').fillna(0).sort_values(by=['weekday', 'hour']).reset_index(drop='index')
        return df1

    def tz_util(self, df, weekday, timezone):
        # 선택 요일, 선택 타임존 이용률
        df1 = df[df['weekday'] == weekday]
        if timezone == info.dc_tz[0]:
            start_hour = 0
            end_hour = 6
        elif timezone == info.dc_tz[1]:
            start_hour = 6
            end_hour = 13
        elif timezone == info.dc_tz[2]:
            start_hour = 13
            end_hour = 18
        else:
            start_hour = 18
            end_hour = 24
        tz_util = round(df1[(df1['hour'] >= start_hour) & (df1['hour'] < end_hour)]['utilization'].sum(), 1)
        return tz_util

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
        # self.check_util_outlier(data)
        util_division = []
        arr_data = []
        if not isinstance(data, list):
            arr_data.append(data)
            data = arr_data

        for n in data:
            if (n > 1.0) and (n <= 2.8):
                util_division.append(2)
            elif (n > 2.8) and (n <= 4.2):
                util_division.append(3)
            elif (n > 4.2) and (n <= 5.6):
                util_division.append(4)
            elif (n > 5.6) and ((n <= 6.9) | (n <= np.round(np.mean(data), 2))):
                util_division.append(5)
            elif n > 6.9:
                util_division.append(6)
            else:
                util_division.append(1)
        return util_division

    def num_users(self, df, *args): # 회원번호, 비회원번호 count하여 이용자 수 계산
        df1_group = df.groupby(['member_number', *args]).size().reset_index(name='cnt')
        df1 = df1_group.groupby([*args])['member_number'].count().reset_index(name='mem_cnt')
        df2_group = df.groupby(['nonmember_number', *args]).size().reset_index(name='cnt')
        df2 = df2_group.groupby([*args])['nonmember_number'].count().reset_index(name='nonmem_cnt')
        df3 = pd.merge(df1, df2, on=[*args], how='outer').fillna(0)
        df3['user_cnt'] = df3['mem_cnt'] + df3['nonmem_cnt']
        return df3

