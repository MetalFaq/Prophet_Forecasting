from fbprophet import Prophet

def pre_calentamiento (m):
    res = {}
    for pname in ['k', 'm', 'sigma_obs']:
        res[pname] = m.params[pname][0][0]
    for pname in ['delta', 'beta']:
        res[pname] = m.params[pname][0]
    return res

def modelo (data_oneyear, data_train, data_test):
    '''
    modelo_tuneado = Prophet(growth= 'linear',
                             n_changepoints = 70,
                             changepoint_range=0.98,
                             yearly_seasonality = False,
                             weekly_seasonality=False,
                             daily_seasonality = False,
                             seasonality_mode = 'additive',
                             seasonality_prior_scale=0.01,     #rango recomendado: 0.01 to 10
                             changepoint_prior_scale = 0.3,  #rango recomendado: 0.001 to 0.5
                             )

    Yearly F: 15 / Weakly F: 5 / Daily F: 3
    MAPE: ¿¿?? %
    '''

    mod_inicial = Prophet(growth='linear',
                          n_changepoints=75,
                          changepoint_range=0.90,
                          yearly_seasonality=False,
                          weekly_seasonality=False,
                          daily_seasonality=False,
                          seasonality_mode='multiplicative',
                          seasonality_prior_scale=0.01,  # rango: 0.01 a 10
                          holidays_prior_scale=5,      # rango: * to 10
                          changepoint_prior_scale=0.35,  # rango: 0.005 a 0.5
                          )

    mod_inicial.add_seasonality(name='yearly', period=365.25, fourier_order=15)
    mod_inicial.add_seasonality(name='weekly_spring',
                                period=7,
                                fourier_order=5,
                                condition_name='is_spring')
    mod_inicial.add_seasonality(name='weekly_summer',
                                period=7,
                                fourier_order=5,
                                condition_name='is_summer')
    mod_inicial.add_seasonality(name='weekly_autumn',
                                period=7,
                                fourier_order=5,
                                condition_name='is_autumn')
    mod_inicial.add_seasonality(name='weekly_winter',
                                period=7,
                                fourier_order=5,
                                condition_name='is_winter')

    mod_inicial.add_seasonality(name='daily_spring',
                                period=1,
                                fourier_order=3,
                                condition_name='is_spring')
    mod_inicial.add_seasonality(name='daily_summer',
                                period=1,
                                fourier_order=3,
                                condition_name='is_summer')
    mod_inicial.add_seasonality(name='daily_autumn',
                                period=1,
                                fourier_order=5,
                                condition_name='is_autumn')
    mod_inicial.add_seasonality(name='daily_winter',
                                period=1,
                                fourier_order=3,
                                condition_name='is_winter')
    mod_inicial.add_seasonality(name='daily_weekend',
                                period=1,
                                fourier_order=3,
                                condition_name='is_weekend')
    mod_inicial.add_seasonality(name='daily_weekday',
                                period=1,
                                fourier_order=3,
                                condition_name='is_weekday')

    mod_inicial.add_regressor(name='temp', prior_scale=5, standardize='auto')
    mod_inicial.add_country_holidays(country_name='AR')

    mod_inicial.fit(data_oneyear)

    '''
    modelo_tuneado = Prophet(growth= 'linear',
                             n_changepoints = 70,
                             changepoint_range=0.98,
                             yearly_seasonality = False,
                             weekly_seasonality=False,
                             daily_seasonality = False,
                             seasonality_mode = 'additive',
                             seasonality_prior_scale=0.01,     #rango recomendado: 0.01 to 10
                             changepoint_prior_scale = 0.3,  #rango recomendado: 0.001 to 0.5
                             )

    Yearly F: 15 / Weakly F: 5 / Daily F: 3
    MAPE: ¿¿?? %
    '''

    mod_final = Prophet(growth='linear',
                        n_changepoints=75,
                        changepoint_range=0.90,
                        yearly_seasonality=False,
                        weekly_seasonality=False,
                        daily_seasonality=False,
                        seasonality_mode='multiplicative',
                        seasonality_prior_scale=0.005,  # rango: 0.01 a 10
                        holidays_prior_scale=5,      # rango: * to 10
                        changepoint_prior_scale=0.35,  # rango: 0.005 a 0.5
                        )

    mod_final.add_seasonality(name='yearly', period=365.25, fourier_order=15)
    mod_final.add_seasonality(name='weekly_spring',
                              period=7,
                              fourier_order=5,
                              condition_name='is_spring')
    mod_final.add_seasonality(name='weekly_summer',
                              period=7,
                              fourier_order=5,
                              condition_name='is_summer')
    mod_final.add_seasonality(name='weekly_autumn',
                              period=7,
                              fourier_order=5,
                              condition_name='is_autumn')
    mod_final.add_seasonality(name='weekly_winter',
                              period=7,
                              fourier_order=5,
                              condition_name='is_winter')

    mod_final.add_seasonality(name='daily_spring',
                              period=1,
                              fourier_order=3,
                              condition_name='is_spring')
    mod_final.add_seasonality(name='daily_summer',
                              period=1,
                              fourier_order=3,
                              condition_name='is_summer')
    mod_final.add_seasonality(name='daily_autumn',
                              period=1,
                              fourier_order=5,
                              condition_name='is_autumn')
    mod_final.add_seasonality(name='daily_winter',
                              period=1,
                              fourier_order=3,
                              condition_name='is_winter')
    mod_final.add_seasonality(name='daily_weekend',
                              period=1,
                              fourier_order=3,
                              condition_name='is_weekend')
    mod_final.add_seasonality(name='daily_weekday',
                              period=1,
                              fourier_order=3,
                              condition_name='is_weekday')

    mod_final.add_regressor(name='temp', prior_scale=5, standardize='auto')
    mod_final.add_country_holidays(country_name='AR')

    mod_final.fit(data_train, init=pre_calentamiento(mod_inicial))
    df_forecast = mod_final.predict(data_test)

    return df_forecast