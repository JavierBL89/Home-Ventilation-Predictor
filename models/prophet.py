from prophet import Prophet
import pandas as pd



def prophet_model(df):
    # Expecting df with timestamp index and a column "indoor_temperature"
    prophet_df = df.copy().reset_index()[["timestamp", "indoor_temperature"]]
    prophet_df.rename(columns={"timestamp": "ds", "indoor_temperature": "y"}, inplace=True)
    
    model = Prophet()
    model.fit(prophet_df)
    
    future = model.make_future_dataframe(periods=48, freq='H')
    forecast = model.predict(future)
    
    # Return the predicted indoor temperatures
    forecast_series = forecast.set_index("ds")["yhat"].tail(48)
    return forecast_series


# we simulate indoor temperature since we do not have it from any source, we use historical data to simulate it
def simulate_indoor_temperature(df):
       # Simulate with some pattern
    import numpy as np
    noise = np.random.normal(loc=1.5, scale=0.5, size=len(df))
    return df["outdoor_temperature"] + noise
