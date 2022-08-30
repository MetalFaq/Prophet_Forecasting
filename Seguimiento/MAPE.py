#Librerias
import pandas as pd
import numpy as np
import os
import requests
import keyboard
import plotly.graph_objects as go
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# y = /Medidor_[num_serie] (split '_' and keep [1]: es el nº de serie)
forecast_path = 'G:/facundo/Escritorio/Prophet_Forecasting/Demanda&Temp/Pronostico_Demanda_48hs'
tipos = ['DMPA', 'DMGA', 'DMWA', 'DTPA', 'DTGA', 'DTWA', 'DIPA', 'DIGA', 'DIWA', 'DLPA', 'DLGA', 'DNPA', 'DNGA']
key = True

def round_minutes (dt,resolution):
    new_minute = (dt.minute // resolution + 1) * resolution
    return dt + timedelta(minutes=new_minute - dt.minute)

# Función del Error Medio Absoluto Porcentual
def mape(y_true, y_pred):
    # conversión a vectores numpy
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    # Porcentaje de error
    pe = (y_true - y_pred) / y_true
    # valor absolutos
    ape = np.abs(pe)
    # Cuantificación del rendimiento en un solo número
    mape = np.mean(ape)
    return f'{mape * 100:.2f}%'

# Recorrido de medidores disponibles para seguimiento. Ya han sido pronosticados.
list = []
for file in os.listdir(forecast_path):
        list.append(int(file.split('_')[1]))

while key:
    ################################################################
    # Usuario ---> Medidor.
    while True:
        id_medidor = input('Ingrese tipo y nº de serie: \n').upper()
        if (len(id_medidor) == 12) and (id_medidor[:4] in tipos):
            serie = int(id_medidor[4:])
            if serie in list:
                name_file = 'Forecast_48hs_' + str(serie) + '.csv'
                print(f'Archivo disponible: {name_file}\n')
                break
            else:
                print('Medidor no disponible')
        else:
            print('Intente nuevamente por favor')

    # Busco el archivo disponible y lo conformo en un dataset.
    df_follow = pd.read_csv(forecast_path + f'/Medidor_{serie}'+ '/' + name_file)
    df_follow['datetime'] = pd.to_datetime(df_follow['datetime'])
    df_follow = df_follow.set_index('datetime')

    data_range = pd.date_range(start = min(df_follow.index),
                               end = max(df_follow.index),
                               freq = '15min')

    df_follow = df_follow.reindex(data_range)
    # print(comb.index.freq)
    # print(f'{comb.isnull().sum()}\n')

    # print(f'{df_follow.head()}\n')
    # print(f'{df_follow.index.min()} --- {df_follow.index.max()}')
    # print(f'{df_follow.shape[0]}')

    ################################################################
    # Usuario ---> Fecha desde donde empezar.
    while True:
        print(f'Ingrese una fecha anterior a: --- {min(df_follow.index)} ---')
        user_date = input('Formato YYYY-MM-DD HH:MM ')
        try:
            datetime_object = datetime.strptime(user_date, '%Y-%m-%d %H:%M')
            desde = round_minutes(datetime_object, 15)
            if desde <= min(df_follow.index):
                break
        except:
            print('\n')
            print('Formato no coincide con lo requerido...\n')

    ################################################################
    # Variables de uso para las API
    TOKEN = "MTQyNjUqJiM5OTAwKiYjREVNTzMqJiMxNzIuMTAuMTAuMzMsMTQzM1xcbXJkaW1zKiYjNzgqJiMxOTI2MDQxMzg1OTM3NDE5MTU5KiYjMiomIy0yMTM3NDc5OTI3"
    basic = HTTPBasicAuth('Discar', 'D1sc4r') # {user, pass}
    dist = 30  #[km]
    quarter = 0

    inicio = desde.isoformat(sep='T')
    hasta = datetime.strptime(str(df_follow.index.max()), '%Y-%m-%d %H:%M:%S').isoformat(sep='T')

    ############################
    # CONSUMO
    ############################
    url = "https://api.mrdims.com/V2/api/Consumos"
    demanda = requests.get(f"{url}?token={TOKEN}&numeroDeSerie={id_medidor}&desde={inicio}&hasta={hasta}&agrupadoPor={quarter}&incluirNulos={False}").json()

    # Conformo mi set de datos de demanda
    consumo_api = pd.DataFrame(demanda, columns=['FechaHora', 'Activa'])
    consumo_api.rename(columns = {'FechaHora' : 'datetime', 'Activa' : 'y[kW]' }, inplace = True)

    # Conversión a formato 'datetime'
    consumo_api['datetime'] = pd.to_datetime(consumo_api['datetime'])
    consumo_api.sort_values(by=['datetime'], axis=0, ascending=True, inplace=True)
    consumo_api.reset_index(inplace=True, drop=True)
    consumo_api = consumo_api.set_index('datetime')

    # print(f'{consumo_api.index.min()} --- {consumo_api.index.max()}')
    # print(f'Datos: {consumo_api.shape[0]}')

    #############################
    # CLIMA
    #############################
    url_medidor = "https://api.mrdims.com/V2/api/Terminales/"
    coordenadas = requests.get(f"{url_medidor}{serie}?token={TOKEN}").json()
    lat = coordenadas['DatosSuministro']['Ubicacion']['LatitudD']
    lon = coordenadas['DatosSuministro']['Ubicacion']['LongitudD']
    #############################################################################
    url_sdm = 'https://apisdm.mrdims.com/api/'
    city = requests.get(f'{url_sdm}Ciudades?lat={lat}&lon={lon}&dist={dist}', auth=basic).json()
    id_city = city[0]['idCiudad']
    #############################################################################
    clima = requests.get(f'{url_sdm}Ciudades/{id_city}/Currents?fechaHoraDesde={inicio}&fechaHoraHasta={hasta}', auth=basic).json()

    # Conformo mi set de datos de clima
    data_weather = pd.DataFrame(clima, columns=['temp', 'horaLocalidad'])
    data_weather.rename(columns={'horaLocalidad': 'datetime'}, inplace=True)

    # Conversión a formato 'datetime'
    data_weather['datetime'] = pd.to_datetime(data_weather['datetime'])
    data_weather['datetime'] = data_weather['datetime'].dt.round('min')
    data_weather.sort_values(by=['datetime'], axis = 0, ascending = True, inplace = True)
    data_weather.reset_index(inplace = True, drop = True)

    # Los minutos del df del clima no son exactos periodos de cuartos de hora, el siguiente bloque corrige eso.
    lista = []
    for date in data_weather['datetime']:
        resolusion = round_minutes(date, 15)
        lista.append(resolusion)

    data_weather['new_datetime'] = lista
    data_weather.drop(columns='datetime', inplace=True)
    data_weather.drop_duplicates(subset = 'new_datetime', keep = 'last', inplace = True)
    data_weather.rename(columns={'new_datetime':'datetime'}, inplace = True)
    data_weather = data_weather.set_index('datetime')

    # print(f'{data_weather.index.min()} --- {data_weather.index.max()}')
    # print(f'Datos: {data_weather.shape[0]}')

    ##################################################################
    # Combinando: demanda y clima actuales
    ##################################################################
    comb = data_weather.copy()
    # agrego la columna de temperaturas
    comb['y[kW]'] = consumo_api['y[kW]']
    comb = comb[['y[kW]', 'temp']]

    data_range = pd.date_range(start = min(comb.index),
                               end = max(comb.index),
                               freq = '15min')

    comb = comb.reindex(data_range)
    # print(comb.index.freq)
    comb['temp'].interpolate(method='linear', inplace=True)
    comb['y[kW]'].interpolate(method='linear', inplace=True)
    # print(f'{comb.isnull().sum()}\n')

    # print('\t\t\t\tINFORMACIÓN ACTUAL DEMANDA & CLIMA \n')
    # print(f'{comb.head()}\n')
    # print(f'{comb.index.min()} --- {comb.index.max()}')
    # print(f'{comb.shape[0]}')

    ################################################################
    # Graficas
    ################################################################
    path = f'./Graficos_{id_medidor}'
    if not os.path.exists(path):
        os.mkdir(path)
        print('Guardando imágenes...')
    else:
        print('Guardando imágenes...')

    # Clima
    fig_clima = go.Figure()
    fig_demanda = go.Figure()
    # Add traces
    fig_clima.add_trace(
        go.Scatter(x=df_follow.index, y=df_follow['Pronostico Clima'], name="Pronostico_Clima")
    )

    fig_clima.add_trace(
        go.Scatter(x=comb.index, y=comb['temp'], name="Clima_Real")
    )

    # Add figure title
    fig_clima.update_layout(
        title_text=f"Comparación Clima {id_medidor}"
    )

    # Set x-axis title
    fig_clima.update_xaxes(title_text=f"Error: {mape(comb['temp'][df_follow.index.min():], df_follow['Pronostico Clima'][:comb.index.max()])}")
    fig_clima.write_image(path + '/' + 'Clima_' + str(serie) + '.png')

    # Consumo
    fig_demanda.add_trace(
        go.Scatter(x=df_follow.index, y=df_follow['Demanda pronosticada en [kW]'], name="Demanda pronosticada")
    )

    fig_demanda.add_trace(
        go.Scatter(x=comb.index, y=comb['y[kW]'], name="Consumo de demanda real")
    )

    # Add figure title
    fig_demanda.update_layout(
        title_text=f"Comparación Demanda {id_medidor}"
    )

    # Set x-axis title
    fig_demanda.update_xaxes(title_text=f"Error: {mape(comb['y[kW]'][df_follow.index.min():], df_follow['Demanda pronosticada en [kW]'][:comb.index.max()])}")
    fig_demanda.write_image(path + '/' + 'Demanda_' + str(serie) + '.png')

    ##################################################################
    # Opciones:
    ##################################################################

    print('##############################################')
    print('Si desea repetir, presione ENTER.')
    print('En caso contrario, presione cualquier tecla.')

    if keyboard.read_key() == 'enter':
        continue
    else:
        key = False