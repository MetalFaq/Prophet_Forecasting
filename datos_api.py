# coding: utf-8
# Combinación en .csv de los datos de: Demanda y Clima (obtenidos directos desde las API's)

#Librerias
import os
import keyboard
import pandas as pd
from datetime import timedelta
from MrDims_API import consumos, city_weather
from API_Forecast_Weather import tratamiento_pronostico

# Función para redondear los minutos de los datos del clima a múltiplos de 15
def round_minutes (dt,resolution):
    new_minute = (dt.minute // resolution + 1) * resolution
    return dt + timedelta(minutes=new_minute - dt.minute)

# *******************************************************
# Variables
key = True
path = "./Train_Data_API"
tipos = ['DMPA', 'DMGA', 'DMWA', 'DTPA', 'DTGA', 'DTWA', 'DIPA', 'DIGA', 'DIWA', 'DLPA', 'DLGA', 'DNPA', 'DNGA']
# *******************************************************

while key:
    ############################################################
    # Usuario
    ############################################################
    while True:
        id_medidor = input('Ingrese tipo y nº de serie del medidor: ').upper()
        if len(id_medidor) == 12 and (id_medidor[:4] in tipos):
            # TIPO[nº de serie: ########]
            id_num = int(id_medidor[4:])
            break
        else:
            print('Intente nuevamente por favor.')

    ############################################################
    # Lectura y configuración de demanda (si el medidor no existe?)
    ############################################################
    demanda = consumos(id_medidor)

    # Conformo mi set de datos de demanda
    data_energy = pd.DataFrame(demanda, columns=['FechaHora', 'Activa'])
    data_energy.rename(columns = {'FechaHora' : 'datetime', 'Activa' : 'y[kW]' }, inplace = True)

    # Conversión a formato 'datetime'
    data_energy['datetime'] = pd.to_datetime(data_energy['datetime'])
    data_energy.sort_values(by=['datetime'], axis = 0, ascending = True, inplace = True)
    data_energy.reset_index(inplace = True, drop = True)

    # Tratamiento de datos
    data_energy.drop_duplicates(subset='datetime', keep = 'last', inplace = True)
    data_energy.set_index('datetime', inplace=True)

    print('\t\t\t\t\t\tINFORMACIÓN DEMANDA [kWh]')
    # print(f'{data_energy.info()}\n')
    print(f'Fecha medición inicial: {data_energy.index.min()}')
    print(f'Fecha medición final : {data_energy.index.max()}\n')
    # data_energy.to_csv('energy_api.csv', encoding='utf-8')

    ############################################################
    # Lectura y configuración del clima
    ############################################################
    '''
    CLIMA:
    GET Terminales & nº de serie ----> datos: long, lat.  
    GET Ciudades & lat, long y dist (30km) ----> ID de la ciudad. 
    GET Ciudades_Currents?fecha:hora & ID de la ciudad ---> datos del clima 
    (Saco datos de temp con dos métodos distintos: desde/hasta OR fecha/hs)
    '''
    clima = city_weather(id_num, 'actual')

    # Conformo mi set de datos de clima
    data_weather = pd.DataFrame(clima, columns=['temp', 'horaLocalidad'])
    data_weather.rename(columns = {'horaLocalidad' : 'datetime'}, inplace = True)

    # Conversión a formato 'datetime'
    data_weather['datetime'] = pd.to_datetime(data_weather['datetime'])
    data_weather['datetime'] = data_weather['datetime'].dt.round('min')
    data_weather.sort_values(by=['datetime'], axis = 0, ascending = True, inplace = True)
    data_weather.reset_index(inplace = True, drop = True)

    # Los minutos del df del clima no son exactos periodos de cuartos de hora, el siguiente for corrige eso.
    lista = []
    for date in data_weather['datetime']:
        resolusion = round_minutes(date, 15)
        lista.append(resolusion)

    data_weather['new_datetime'] = lista
    data_weather.drop(columns='datetime', inplace=True)
    data_weather.drop_duplicates(subset = 'new_datetime', keep = 'last', inplace = True)
    weather = data_weather.set_index('new_datetime')

    print('\t\t\t\t\t\tINFORMACIÓN CLIMA [ºT]')
    # print(f'{weather.info()}\n')
    print(f'Fecha medición inicial: {weather.index.min()}')
    print(f'Fecha medición final : {weather.index.max()}\n')
    # weather.to_csv('weather_api.csv', encoding='utf-8')

    ##################################################################
    # Combinando: demanda y clima
    ##################################################################
    data_comb = data_energy.loc['2021-04-12 08:45:00':].copy()
    # agrego la columna de temperaturas
    data_comb['temp'] = weather['temp']

    # Custom range
    data_range = pd.date_range(start = min(data_comb.index),
                               end = max(data_comb.index),
                               freq = '15min')

    full_comb = data_comb.reindex(data_range)
    # print(f'La frecuencia de la serie de datos es: {full_comb.index.freq}\n')
    # print('\t\t\t\t\t\tINFORMACIÓN DEMANDA & CLIMA \n')
    # print(f'{full_comb.info()}\n')
    # print('Cantidad de datos nulos: ')
    # print(f'{full_comb.isnull().sum()}\n')

    # Llenamos estos valores blancos con valores que se encuentran en una curva lineal entre puntos de datos existentes
    full_comb['temp'].interpolate(method='linear', inplace=True)
    full_comb['y[kW]'].interpolate(method='linear', inplace=True)
    # print(f'Datos nulos (dsp de interpolar): \n{full_comb.isnull().sum()}\n')

    print('Datos combinados correctamente\n')
    # print(f'{full_comb.info()}\n')

    ##################################################################
    # Archivo combinado .csv de salida:
    ##################################################################
    if not os.path.exists(path):
        os.mkdir(path)
        print('Un nuevo directorio p/almacenar los datos de entrenamiento ha sido creado\n')
        print(f'Datos de entrenamiento guardados en {path}...\n')
    else:
        print(f'Archivo de entrenamiento guardado en {path}...\n')

    file_name = 'Datos_' + str(id_num) + '.csv'
    full_comb['datetime'] = full_comb.index
    full_comb.to_csv(path + '/' + file_name, index=False, encoding='utf-8')
    # print(f'Datos guardados en {path}\n')

    ##################################################################
    # Datos del clima para la predicción: Pronóstico de datos en 48hs
    ##################################################################

    weather_forecast = city_weather(id_num, 'futuro')
    set_test = tratamiento_pronostico(id_num, weather_forecast)

    ##################################################################
    # Opciones:
    ##################################################################

    print('##############################################')
    print('Si desea cargar nuevos datos, presione ENTER.')
    print('En caso contrario, presione cualquier tecla.')

    if keyboard.read_key() != 'enter':
        key = False