import pandas as pd
import numpy as np
import os
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
        self.df['isWeek'] =  self.df['weekday'].apply(lambda x: 1 if x > 4 else 0)
        return self.df

    def add_columns(self):
        self.time_split('chStartTm')
        # self.df['chTm'] = (self.df['chStartTm'] - self.df['chEndTm']).dt.total_seconds()
        # self.df = self.df.astype({'chTm': int})
        self.df['userType'] = np.where(self.df['userName'] != '비회원', '회원',np.where(self.df['rmCardEntity'].notnull().values == True, '로밍회원', '비회원'))  # 회원유형 구분
        return self.df

    def charger_avg_stat(self, df, *args):
        df_grouped = df.groupby([*args, 'date'])
        df1 = df_grouped[['chTm2', 'totEnergy']].apply(sum).reset_index()
        df1['utz'] = round(df1['chTm2'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby([*args]).mean().reset_index(), 1)

        if 'weekday' in args and 'hour' in args:
            df2 = self.set_weekday_hour(df2)
        return df2

    def charger_sum_stat(self, df, *args):
        df_grouped = df.groupby([*args])
        df1 = df_grouped[['chTm2', 'totCost', 'totEnergy']].apply(sum).reset_index()
        return df1

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
        tz_util = round(df1[(df1['hour'] >= start_hour) & (df1['hour'] < end_hour)]['utz'].sum(), 1)
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
            timezone_sum = df.groupby('timezone')['utz'].sum()
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

    def score_num_users(self, data):
        num_user_division = []
        avg = data.mean()

        for n in data:
            if n < avg :
                num_user_division.append(info.num_users[0][0])
            else:
                num_user_division.append(info.num_users[1][0])
        return num_user_division

    def num_users(self, df, *args): # 회원번호, 비회원번호 count하여 이용자 수 계산
        df1_group = df.groupby(['memberNo', *args]).size().reset_index(name='cnt')
        df1 = df1_group.groupby([*args])['memberNo'].count().reset_index(name='memberCnt')
        df2_group = df.groupby(['nonMemberNo', *args]).size().reset_index(name='cnt')
        df2 = df2_group.groupby([*args])['nonMemberNo'].count().reset_index(name='nonMemberCnt')
        df3 = pd.merge(df1, df2, on=[*args], how='outer').fillna(0)
        df3['userCnt'] = df3['memberCnt'] + df3['nonMemberCnt']
        return df3

    def score_chplace(self, data):
        place_division = []

        for n in data:
            if n == info.accessibility[0][1]:
                place_division.append(info.accessibility[0][0])
            elif n == info.accessibility[1][1]:
                place_division.append(info.accessibility[1][0])
            elif n == info.accessibility[2][1]:
                place_division.append(info.accessibility[2][0])
            elif n == info.accessibility[3][1]:
                place_division.append(info.accessibility[3][0])
            else:
                place_division.append(info.avg_num_users[4][0])
        return place_division

    def exist_path(self, *args):
        imgPath = '../../img/'
        placePath = imgPath + args[0].replace('/', '-')
        path = placePath
        if not os.path.exists(placePath):
            os.mkdir(placePath)

        if(len(args) > 1):
            evsePath = placePath + '/' + str(args[1])
            path = evsePath
            if not os.path.exists(evsePath):
                os.mkdir(evsePath)
        return path



