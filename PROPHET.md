## 📈 Prophet Model for Time-Series Forecasting
Facebook Prophet is an open-source time-series forecasting tool developed by Meta. 

It is a powerful forecasting tool built for data with strong trends and seasonal patterns. It is ideal for real-world scenarios like predicting temperatures, energy usage, or traffic—where seasonality and sudden trend shifts occur

## 🔹 Why Use Prophet?

- Handles seasonality automatically (daily, weekly, yearly).
- Tolerant to missing data and outliers.
- Easy to use and great for business time series (like temperature, demand, or traffic).
- Makes forecasts that are interpretable and robust.

## 🔍 How Prophet Works
Prophet breaks a time series into 3 main components:

| Component	         | What it means |
|Trend	             | The overall direction (up/down) of the data over time.|
| Seasonality        | Repeating patterns (e.g., cooler nights, warmer afternoons).|


## 📚 Preparing Data for Prophet
Prophet needs a DataFrame with 2 columns:


- ds	Date or timestamp (datetime format)
- y	    The value you want to predict (e.g., indoor temperature)

```python
prophet_df = df.reset_index()[["timestamp", "indoor_temperature"]]
prophet_df.rename(columns={"timestamp": "ds", "indoor_temperature": "y"}, inplace=True)
```

## Training the Model
```python
from prophet import Prophet

model = Prophet()
model.fit(prophet_df)
```


## 🔮 Making Predictions
```python
# Create future timestamps
future = model.make_future_dataframe(periods=48, freq="H")  # next 48 hours

# Predict
forecast = model.predict(future)

# Get just the predicted values
forecast_series = forecast.set_index("ds")["yhat"].tail(48)
```

## Visualizing the Forecast
```python
model.plot(forecast);
model.plot_components(forecast);

```