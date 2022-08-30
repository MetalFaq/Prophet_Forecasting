'''
Links con acceso a las API disponibles:

#produccion
https://api.mrdims.com/V2/Help

#clima
https://apisdm.mrdims.com/Help

Las API devuelven desde y hasta la fecha que tengan datos disponibles. Tener en cuenta!!
'''

import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime

# 12/04/2021: Fecha desde la que están disponibles los datos del clima
desde = datetime(2021, 4, 12, 0, 0, 0).isoformat(sep='T')
hasta = datetime.now().isoformat(sep='T')

# Variables de uso para las API
TOKEN = "MTQyNjUqJiM5OTAwKiYjREVNTzMqJiMxNzIuMTAuMTAuMzMsMTQzM1xcbXJkaW1zKiYjNzgqJiMxOTI2MDQxMzg1OTM3NDE5MTU5KiYjMiomIy0yMTM3NDc5OTI3"
basic = HTTPBasicAuth('Discar', 'D1sc4r') # {user, pass}
dist = 30  # [km]
quarter = 0

def consumos (user):
    url = "https://api.mrdims.com/V2/api/Consumos"
    demanda = requests.get(f"{url}?token={TOKEN}&numeroDeSerie={user}&desde={desde}&hasta={hasta}&agrupadoPor={quarter}&incluirNulos={False}").json()
    return demanda

def city_weather (n_serie,other):
    url_medidor = "https://api.mrdims.com/V2/api/Terminales/"
    coordenadas = requests.get(f"{url_medidor}{n_serie}?token={TOKEN}").json()
    lat = coordenadas['DatosSuministro']['Ubicacion']['LatitudD']
    lon = coordenadas['DatosSuministro']['Ubicacion']['LongitudD']
    #############################################################################
    url_sdm = 'https://apisdm.mrdims.com/api/'
    city = requests.get(f'{url_sdm}Ciudades?lat={lat}&lon={lon}&dist={dist}', auth=basic).json()
    id_city = city[0]['idCiudad']
    #############################################################################
    if other == 'actual':
        clima = requests.get(f'{url_sdm}Ciudades/{id_city}/Currents?fechaHoraDesde={desde}&fechaHoraHasta={hasta}', auth=basic).json()
        return clima

    if other == 'futuro':
        weather_forecast = requests.get(f'{url_sdm}Ciudades/{id_city}/Forecasts', auth=basic).json()
        return weather_forecast
