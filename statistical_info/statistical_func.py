import pandas as pd
import numpy as np
from common import info

class base:
    def __init__(self, df):
        self.df = df

    def regional_info(self):
        df = self.df
        df_grouped = df.groupby(['charger_region', 'station_name', 'charger_code', 'date'])
        df1 = df_grouped[['charging_time', 'charging_capacity']].apply(sum).reset_index()
        df1['utilization'] = round(df1['charging_time'].apply(lambda x: x / (24 * 60 * 60) * 100), 2)
        df2 = round(df1.groupby('charger_region').mean().reset_index(), 1)
        df2['charging_time'] = round(df2['charging_time'] / 60, 2)
        return df2
