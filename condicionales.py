import pandas as pd

# Funciones condicionales debido al comportamiento estacionario de los datos
def is_spring(ds):
    date = pd.to_datetime(ds)
    return (date.month >= 3) & (date.month <=5)

def is_summer(ds):
    date = pd.to_datetime(ds)
    return (date.month >= 6) & (date.month <=8)

def is_autumn(ds):
    date = pd.to_datetime(ds)
    return (date.month >= 9) & (date.month <=11)

def is_winter(ds):
    date = pd.to_datetime(ds)
    return (date.month == 12) | (date.month <=2)

def is_weekend(ds):
    return ds.dayofweek in (5, 6)

def calentamiento_estaciones(data_oneyear):
    data_oneyear['is_spring'] = data_oneyear['ds'].apply(is_spring)
    data_oneyear['is_summer'] = data_oneyear['ds'].apply(is_summer)
    data_oneyear['is_autumn'] = data_oneyear['ds'].apply(is_autumn)
    data_oneyear['is_winter'] = data_oneyear['ds'].apply(is_winter)
    data_oneyear['is_weekend'] = data_oneyear['ds'].apply(is_weekend)
    data_oneyear['is_weekday'] = ~data_oneyear['ds'].apply(is_weekend)
    return data_oneyear

def train_estaciones(data_train):
    data_train['is_spring'] = data_train['ds'].apply(is_spring)
    data_train['is_summer'] = data_train['ds'].apply(is_summer)
    data_train['is_autumn'] = data_train['ds'].apply(is_autumn)
    data_train['is_winter'] = data_train['ds'].apply(is_winter)
    data_train['is_weekend'] = data_train['ds'].apply(is_weekend)
    data_train['is_weekday'] = ~data_train['ds'].apply(is_weekend)
    return data_train

def test_estaciones(data_test):
    data_test['is_spring'] = data_test['ds'].apply(is_spring)
    data_test['is_summer'] = data_test['ds'].apply(is_summer)
    data_test['is_autumn'] = data_test['ds'].apply(is_autumn)
    data_test['is_winter'] = data_test['ds'].apply(is_winter)
    data_test['is_weekend'] = data_test['ds'].apply(is_weekend)
    data_test['is_weekday'] = ~data_test['ds'].apply(is_weekend)
    return data_test
