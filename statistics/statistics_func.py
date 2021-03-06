import pandas as pd
import numpy as np
from common import info

class base:
    def __init__(self, df):
        self.df = df

    def variable_avg_stat(self, df, *args):
        df_grouped = df.groupby(['station_name', 'charger_code', 'date', *args])
        df1 = df_grouped[['charging_time', 'charging_capacity']].apply(sum).reset_index()
        df1['charging_cnt'] = df_grouped.size().reset_index(name='cnt')['cnt']
        df1['utz'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby([*args]).mean().reset_index(), 1)
        df2['charging_time'] = round(df2['charging_time'] / 60, 0)
        return df2

    def charger_sum_stat(self, *args):
        df_grouped = self.df.groupby([*args])
        df1 = df_grouped[['totCost', 'totEnergy']].apply(sum).reset_index()
        return df1

    def num_users(self, df, *args): # 회원번호, 비회원번호 count하여 이용자 수 계산
        df1_group = df.groupby(['station_name', 'charger_code', 'member_number', *args]).size().reset_index(name='cnt')
        df1 = df1_group.groupby(['station_name', 'charger_code', *args])['member_number'].count().reset_index(name='mem_cnt')
        df2_group = df.groupby(['station_name', 'charger_code', 'nonmember_number', *args]).size().reset_index(name='cnt')
        df2 = df2_group.groupby(['station_name', 'charger_code', *args])['nonmember_number'].count().reset_index(name='nonmem_cnt')
        df3 = pd.merge(df1, df2, on=['station_name', 'charger_code', *args], how='outer').fillna(0)
        df3['user_cnt'] = df3['mem_cnt'] + df3['nonmem_cnt']
        return df3

