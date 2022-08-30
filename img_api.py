import plotly.graph_objects as go

def dali(serie, train, test, forecast, path_1):

    # create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train[-len(test):].ds, y=train[-len(test):].y,
                             mode='lines',
                             name='Test - Ground Truth'))
    fig.add_trace(go.Scatter(x=forecast.ds, y=forecast.yhat,
                             mode='lines',
                             name='Prediction'))

    # adjust layout
    fig.update_traces(line=dict(width=0.5))
    fig.update_layout(title=f'Prophet Forecast: Demanda [kWh] | Terminal {serie}',
                      xaxis_title='Date & Time',
                      yaxis_title='Demanda de energía [kWh]')

    file_name = serie + '.png'
    fig.write_image(path_1 + '/' + file_name)
