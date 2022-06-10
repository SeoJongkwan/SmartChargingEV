import pandas as pd
import numpy as np
from common import info

class base:
    def __init__(self, df):
        self.df = df

    def variable_avg_stat(self, *args):
        df = self.df
        df_grouped = df.groupby(['station_name', 'charger_code', 'date', *args])
        df1 = df_grouped[['charging_time', 'charging_capacity']].apply(sum).reset_index()
        df1['utilization'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby([*args]).mean().reset_index(), 2)
        df2['charging_time'] = round(df2['charging_time'] / 60, 2)
        return df2

    def num_users(self, df, *args): # 회원번호, 비회원번호 count하여 이용자 수 계산
        gp_mem = df.groupby(['station_name', 'charger_code', 'month', 'member_number', *args]).size().reset_index(name='cnt')
        member_num = gp_mem.groupby(['month', *args])['member_number'].count().reset_index(name='mem_cnt')
        gp_nonmem = df.groupby(['station_name', 'charger_code', 'month', 'nonmember_number', *args]).size().reset_index(name='cnt')
        nonmember_num = gp_nonmem.groupby(['month', *args])['nonmember_number'].count().reset_index(name='nonmem_cnt')
        df1 = pd.merge(member_num, nonmember_num, on=['month', 'wd_rank' ], how='inner')
        df1['cnt'] = df1['mem_cnt'] + df1['nonmem_cnt']
        return df1

    def util_stat(self, *args):
        df = self.df
        df_grouped = df.groupby(['station_name', 'charger_code', 'month', 'date', *args])
        df1 = df_grouped[['charging_time', 'charging_capacity']].apply(sum).reset_index()
        df1['utilization'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby([*args]).mean().reset_index(), 2)
        df2['charging_time'] = round(df2['charging_time'] / 60, 2)
        return df2



