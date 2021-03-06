# -*- coding: utf-8 -*-
"""TestingFile_EnergyConsumption.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1okJu-_LoLyi9zodNTGnicbiUk7BjOfBw
"""

import pandas as pd
import time
import numpy as np
import datetime
import logging
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline
logging.debug('Loading libraries for feature selection and prediction')
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestRegressor
from math import sqrt
import joblib


df_loaded = pd.read_csv("TestingData2_EnergyConsumption.csv",parse_dates=['date'])
df = df_loaded
    


df.head()

df['NSM'] = df.date.apply(lambda x: x.hour*3600 + x.minute*60 +x.second)
df['day_of_week'] = df.date.apply(lambda x: x.dayofweek)
df['week_status'] = df.day_of_week.apply(lambda x: 0 if (x == 5 or x == 6) else 1)

shape_bool = df.date.nunique() == df.shape[0]


all_columns = df.columns.tolist()

df_describe = df.describe().T

df_describe['Interquartile Range'] = 1.5*(df_describe['75%'] - df_describe['25%'])
df_describe['Major Outlier'] = (df_describe['75%'] + df_describe['Interquartile Range'])
df_describe['Minor Outlier'] = (df_describe['25%'] - df_describe['Interquartile Range'])


def remove_outlier(df, variable):
    major_o = df_describe.loc[variable,'Major Outlier']
    minor_o = df_describe.loc[variable,'Minor Outlier']
    df = df.drop(df[(df[variable]>major_o) | (df[variable]<minor_o)].index)
    return df

outlier_column_list = [x for x in all_columns 
                       if x not in ('date', 'Appliances', 'lights')]


for column_name in outlier_column_list:
    df = remove_outlier(df, column_name)

dropped = ((df_loaded.shape[0] - df.shape[0])/df_loaded.shape[0])*100


week_status = pd.get_dummies(df['week_status'], prefix = 'week_status')
day_of_week = pd.get_dummies(df['day_of_week'], prefix = 'day_of_week')

df = pd.concat((df,week_status),axis=1)
df = pd.concat((df,day_of_week),axis=1)

df = df.drop(['week_status','day_of_week'],axis=1)

df = df.rename(columns={'week_status_0': 'Weekend', 'week_status_1': 'Weekday',
                   'day_of_week_0': 'Monday', 'day_of_week_1': 'Tuesday', 'day_of_week_2': 'Wednesday',
                  'day_of_week_3': 'Thursday', 'day_of_week_4': 'Friday', 'day_of_week_5': 'Saturday',
                  'day_of_week_6': 'Sunday'})

df['Appliances'] = df['Appliances'] + df['lights']
df = df.drop(['lights'],axis=1)
df = df.drop(['date'],axis=1)

X = df.drop(['Appliances'],axis=1)
y = df['Appliances']
X.head()

# Load the model from the file 
loaded_model = joblib.load('Energy_Consumption.pkl')

# Use the loaded model to make predictions 
y_pred = loaded_model.predict(df) 
print(y_pred)



