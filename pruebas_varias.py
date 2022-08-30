import os

forecast_path = 'Demanda&Temp/Pronostico_Demanda_48hs'

list = []
for file in os.listdir(forecast_path):
        list.append(int(file.split('_')[1]))
print(list)
print(type(list[3]))
