# Prophet_Forecasting

## Objetivo
Lograr pronosticar los posibles valores de demanda de energía activa [kW/h] en la ciudad de Gálvez, Santa Fe. <br>
Para ello se cuenta con los siguientes datos:
<ul>
<li>Datos de consumo pasado</li>
<li>Datos del clima (desde 12/04/2021)</li>
</ul>

## Elección del modelo
Como un modelo empleado para el análisis y modelado de series de tiempo con datos, Prophet destaca por permitir al usuario
configurar de manera más accesible parámetros como la frecuencia de estacionalidad, flexibilidad en la tendencia, ajuste en los días feriados
y porcentaje de incertidumbre sin necesidad de una base de conocimientos fuertes en matemáticas y estadística. <br>
<br>
La función matemática que lo representa es la siguiente:<br>
<i>y(t) = g(t) + s(t) + h(t) + e(t)</i><br>
<ul>
<li>g(t): factor de tendencia</li>
<li>s(t): componente de estacionalidad</li>
<li>h(t): componente de feriados</li>
<li>e(t): componente de incertidumbre</li>
</ul>
<br>
El uso del modelo es bastante directo: Se importan las librerías necesarias, se cargan los datos a un dataframe, se estudia la información (análisis de características EDA, filtro de info y gráficas). 

## Procedimiento
### Fuente de datos
Se me ha provisto del uso de ciertas API y endpoint para hacer request de datos de consumo de energía del pasado, como para datos del clima y pronóstico del mismo a 48hs que más delante ayudara de manera muy importante para la obtención del pronóstico del demanda. <br>
La información del consumo [kWh] está medida diariamente con mediciones realizadas c/15 minutos. <br>
Gracias a la ayuda de herramientas gráficas se pudo conocer que el comportamiento de los datos demuestra un claro movimiento estacionario y constante a lo largo de los años de medición. <br>
La información brindada sobre el clima está disponible desde el 12/04/2021 y la misma es irregular en cuanto al intervalo de tiempo que se mide (ajuste necesario en este punto). Al tener desde una fecha exacta la info del clima, me ví limitado a tomar desde la misma fecha datos de consumo, dado que de esta manera me era posible tener la misma longitud de datos para hacer uso del clima como herramienta de ayuda. <br>
### Lectura y limpieza de datos
<ul>
  <li>Archivo .csv asigando a un dataframe.</li>
  <li>Analicé al dataframe como una serie de tiempo.</li>
  <li>Verifique que exista una frecuencia de medición, para que en caso de no ser así, realizar una interpolación de datos.</li>
  <li>Filtro digital de suavización "Savitzky-Golay" con el proposito de suavizar la curva de datos en el tiempo.</li> 
</ul>

### EDA y VDA
Con el análisis exploratorio de datos y gráficandolos, pude observar un comportamiento estacional en los meses de primavera y verano con una marcada llanura en los meses correspondientes a otoño e invierno. <br>
<i><b>Conclusión: Modelo estacionario aditivo</i></b>
### Aplicación del modelo
Particioné los datos en set de entrenamiento y otro set para testing (20% - 25% para testing aprox). <br>
Para que Prophet logre hacer su trabajo correctamente, tuve que ajustar el nombre de las columnas dado a que es un requisito tener una columna llamada "ds:datestamp" correspondiente a las fechas en formato: YYYY-MM-DD HH:MM:SS, y la columna "y" que ha de ser numérica y representar la variable a pronosticar. <br>
La estacionalidad puede ser modelada también, por lo que fue reflejado en el programa como funciones de condiciones estacionales. <br>
Con los datos de entrenamiento preparados, se genera una instancia de la clase Prophet, se cargan los datos a entrenar y se gráfica el resultado para observar el <b>MAPE: Error Porcentual Absoluto Medio</b>.
### Ajuste de parámetros
Para obtener menor errores y en base a la devolución del programa luego de correrlo un par de intentos, se ajustaron los parámetros siguientes:
<ul>
  <li>'Growth: Tipo de crecimiento lineal</li>
  <li>n-changepoints: Mayor cantidad de puntos de cambios para el aprendizaje</li>
  <li>seasonality_mode: Aditiva</li>
  <li>changepoint_prior_scale: reducir la flexibilidad de la tendencia</li>
</ul>

### Datos del clima
Uní estos datos con los del consumo, agregando una columna de "temp". <br>
Realicé un analisis de esto, y ajuste las medidas de tiempo como los casos de datos faltantes con interpolación lineal. <br>
La posibilidad de agregar estos datos al modelo de Prophet es posible gracias a la función ".add_regressor". <br>
Corrí el programa con los ajustes por defecto y luego fui modificando para reducir el error a un <10%. 

### Pre-Entrenamiento
Para mitigar el agregado de datos debido a los días que transcurren, inicialmente se ejecuta un pronóstico de datos con una cantidad fija y a este resultado lo cargo en el modelo de pronóstico final. Lamentablemente, esto tiene por efecto aumentar la carga de procesamiento y horaria de la predicción. Aún así, dado que la predicción es para 48hs, unas hs de predicción no es un efecto adverso para el alcance de este proyecto. 

### Corroboración. 
Una vez pasadas las 48 hs, me aseguro de descargar de la API los datos de consumo y compararlos con los datos que obtuve de la predicción. <br>

## Instalación
<b>Es necesario Python 3.9</b>
<ul>
  <li>Git clone en una carpeta que hayas creado para el proyecto</li>
  <li>Crear un entorno virtual dentro de la carpeta del proyecto.<br><b>ES NECESARIO HACERLO EN UN ENTORNO DE CONDA SI O SI PARA QUE 'fbprophet' FUNCIONE</b></li>
  <li>Instalar las dependencias con el entorno activo: pip install -r requirements.txt</li>
</ul>

## Ejecución
<ul>
  <li>Para descargar los datos desde la API, ejecutar: python datos_api.py</li>
  <li>Se genera una carpeta llamada "Train_Data_API" donde se guardan los datos de consumo pasado y el clima de esos días.</li>
  <li>Se genera una carpeta llamada "Pronostico_Clima_API", donde se almacenan los datos del pronostico del clima a 48hs.</li>
  <li>Para llevar a cabo el programa de pronótico, ejecutar: python Forecast_demanda.py</li>
  <li>Se genera una carpeta "Pronostico_Demanda_48hs" donde se guarda un archivo .csv con los datos a futuro y una gráfica que representa el comportamiento de dichos datos.</li>
</ul>

## Comprobaciones
<ul>
  <li>Pasadas las 48hs, ir hasta la carpeta llamada "Seguimiento" y correr: python MAPE.py<br>
      Recomiento que este paso se lleve a cabo desde la PowerShell de Windows (si estás haciendolo desde dicho SO). 
  </li>
  <li>Esto generará una carpeta con el nombre del medidor bajo pronóstico y dentro un archivo con los datos de fecha, consumo y clima junto a un grafico comparando datos reales con datos pronosticados. </li>
<li>En la carpeta "Documentos" no hay nada ejecutable, lo más importante es un excel que he hecho para juntar y graficar alguno de los pronóticos que he hecho</li>
</ul>
