import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from common import info

class base:
    def __init__(self, df):
        self.df = df

    def regional_info(self, column):
        """
        :param column: a column name indicating start time
        :return: a dataframe with (month, date, weekday, hour, minute) column
        """
        return self.df


