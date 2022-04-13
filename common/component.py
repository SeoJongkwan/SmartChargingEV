class base:
    def __init__(self, df):
        self.df = df

    def time_split(self, column):
        """
        :param column: start time
        :return: create time split column
        """
        self.df['month'] = self.df[column].dt.strftime('%Y-%m')
        self.df['date'] = self.df[column].dt.date
        # self.df['weekday'] = self.df[column].dt.weekday
        self.df['day_of_week'] = self.df[column].dt.day_name()
        self.df['hour'] = self.df[column].dt.hour
        self.df['minute'] = self.df[column].dt.minute
        return self.df
