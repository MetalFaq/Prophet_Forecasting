#!/usr/bin/env python
# coding: utf-8

'''
Mejoras y añadidos:
* Guardar clima independiente a este proyecto.
* Almacenar por fecha (o por medidor, y dentro de la carpeta del medidor por fecha) para evitar reemplazar los datos.
'''

############################################
# LIBRERIAS
############################################
import os, sys, keyboard, time
import pandas as pd
from scipy.signal import savgol_filter
from condicionales import train_estaciones, test_estaciones, calentamiento_estaciones
from app_prophet import modelo
from img_api import dali

############################################
# Pronostico Demanda (Prophet)
############################################
data_path = "./Train_Data_API"
weather_path = "./Pronostico_Clima_API"
out_path = './Pronostico_Demanda_48hs'
key = True

while key:
    ############################################################
    # Usuario
    ############################################################
    while True:
        user_input = input('Ingrese número de serie sin tipo: ')
        try:
            num = int(user_input)
            if type(num) == int:
                break
        except:
            print('Nº de serie no valido.\nIntente otra vez...') #generar lista en el arch de datos y comparar

    if not os.path.exists(data_path):
        os.mkdir(data_path)
        # print('El directorio de datos no existía y ha sido creado (EMPTY).\n')
    else:
        print(f'Buscando datos de entrenamiento p/ {num}...\n')

    arch_name = 'Datos_'+user_input+'.csv'

    if arch_name in os.listdir(data_path):
        path_medidor = data_path + '/' + arch_name
        df = pd.read_csv(path_medidor, parse_dates=['datetime'])
        df.sort_values(by=['datetime'], axis=0, ascending=True, inplace=True)
        df.reset_index(inplace=True, drop=True)
        print('\t\t\t\t\t\tINFORMACIÓN GENERAL ')
        print(f'{df.info()}\n')
        print("Variable objetivo: y[kW]\n")
    else:
        print(f'Los datos del medidor {user_input} no existen')
        sys.exit()

    ############################################
    # Filtro sobre y[kW] (normalizar mejor?)
    ############################################
    y_filtered = df[['y[kW]']].apply(savgol_filter,  window_length=5, polyorder=3)
    y_filtered['temp'] = df['temp']
    y_filtered['datetime'] = df['datetime']
    y_filtered['datetime'] = pd.to_datetime(y_filtered['datetime'])
    y_filtered.sort_values(by=['datetime'], axis = 0, ascending = True, inplace = True)
    y_filtered.reset_index(inplace = True, drop = True)

    ############################################
    # Partición de la serie de tiempo
    ############################################
    train = y_filtered.copy()
    train.rename({'datetime': 'ds', 'y[kW]': 'y'}, axis='columns', inplace=True)
    print(f'El entrenamiento comienza desde: {min(train.ds)}')
    print(f'hasta: {max(train.ds)}\n')

    recorte = y_filtered['datetime'][35040]  # un año
    first_year = y_filtered[y_filtered['datetime'] <= recorte].copy()
    first_year.rename({'datetime': 'ds', 'y[kW]': 'y'}, axis='columns', inplace=True)

    name_test = 'Clima_'+user_input+'.csv'
    test = pd.read_csv(weather_path+'/'+name_test, parse_dates=['datetime'])
    test['datetime'] = pd.to_datetime(test['datetime'])
    test.sort_values(by=['datetime'], axis=0, ascending=True, inplace=True)
    test = test.rename({'datetime': 'ds', 'future_temp': 'temp'}, axis='columns')

    print(f'Las próximas 48hs comienza: {min(test.ds)}')

    print(f'hasta: {max(test.ds)}\n')

    ############################################
    # Prophet
    ############################################
    start_time = time.time()

    # Condicionales
    train_estaciones(train)
    test_estaciones(test)
    calentamiento_estaciones(first_year)

    pronostico = modelo(first_year, train, test)
    print(f"--- {(time.time() - start_time):.2f} seconds of Prophet ---")
    ############################################
    # Archivo .csv de salida
    ############################################
    df_out = pd.merge(test[['ds', 'temp']], pronostico[['ds', 'yhat']], on='ds')
    df_out.rename(columns={'ds': 'datetime', 'yhat': 'Demanda pronosticada en [kW]', 'temp': 'Pronostico Clima'},
                  inplace=True)
    df_out = df_out[['datetime', 'Demanda pronosticada en [kW]', 'Pronostico Clima']]
    df_out.set_index('datetime')

    file_name = 'Forecast_48hs_' + user_input + '.csv'
    forecast_file = f'/Medidor_{user_input}'

    if not os.path.exists(out_path):
        os.mkdir(out_path)

    demanda_path = out_path + forecast_file
    if not os.path.exists(demanda_path):
        os.mkdir(demanda_path)

    df_out.to_csv(demanda_path + '/' + file_name, index=False, encoding='utf-8')
    dali(user_input, train, test, pronostico, demanda_path)
    print('Datos y figuras del pronostico de demanda guardados correctamente')

    ##################################################################
    # Opciones:
    ##################################################################
    print('##############################################')
    print('Si desea cargar nuevos datos, presione ENTER.')
    print('En caso contrario, presione cualquier tecla.')

    if keyboard.read_key() != 'enter':
        key = False
