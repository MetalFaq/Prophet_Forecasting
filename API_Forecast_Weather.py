import pandas as pd
import os
path_of_weather = "./Pronostico_Clima_API"

def tratamiento_pronostico (serie, arc_jason):

    two_day_forecast_weather = pd.DataFrame(arc_jason, columns=['temperatura', 'horaLocalidad'])
    two_day_forecast_weather.rename(columns={'horaLocalidad': 'datetime', 'temperatura': 'future_temp'}, inplace=True)
    two_day_forecast_weather['datetime'] = pd.to_datetime(two_day_forecast_weather['datetime'])
    two_day_forecast_weather.sort_values(by=['datetime'], axis=0, ascending=True, inplace=True)
    two_day_forecast_weather.reset_index(inplace=True, drop=True)
    two_day_forecast_weather.drop_duplicates(subset='datetime', keep='last', inplace=True)
    two_day_forecast_weather.set_index('datetime', inplace=True)

    # Rango de tiempo completo.
    periodo = pd.date_range(start=min(two_day_forecast_weather.index),
                            end=max(two_day_forecast_weather.index),
                            freq='15min')

    # Nuevas filas donde sus valores son NaN en favor de tener una frecuencia de datos estable.
    data_test = two_day_forecast_weather.reindex(periodo)
    data_test['future_temp'].interpolate(method='linear', inplace=True)

    print('\t\t\t\t\t\tINFORMACIÓN PRONOSTICO DEL CLIMA (48hs) ')
    # print(f'{data_test.info()}\n')
    print(f'Fecha medición inicial: {data_test.index.min()}')
    print(f'Fecha medición final : {data_test.index.max()}')

    if not os.path.exists(path_of_weather):
        os.mkdir(path_of_weather)
        print('Un nuevo directorio de datos futuros ha sido creado')
        print('Generando archivo...')
    else:
        print('Generando archivo...')

    file_name = 'Clima_' + str(serie) + '.csv'
    data_test['datetime'] = data_test.index
    data_test.to_csv(path_of_weather + '/' + file_name, index=False, encoding='utf-8')
    print(f'Set de datos guardados en {path_of_weather}')


