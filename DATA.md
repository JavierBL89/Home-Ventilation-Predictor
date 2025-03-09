



## Data collection

Features
- Timestamp (hourly)
- Indoor temperature
- Outdoor temperature
- indoor_temp_lag_1h → What was the indoor temperature 1 hour ago?
- indoor_temp_lag_6h → What was it 6 hours ago?
- indoor_temp_lag_24h → What was it yesterday at the same time?

#### Why temp_lag (Lags)?
Buildings retain heat/cool air, so indoor temperature doesn’t instantly match outdoor changes.
There’s a delay in how indoor temperature reacts to outdoor shifts (e.g., a cold front outside doesn’t immediately cool down a house).
Better forecasting – ARIMA, Prophet, and LSTMs can use past indoor temperatures to predict future temperatures more accurately.

**Practical Example**
Imagine at 12 PM:

Outdoor temperature = 30°C.
Indoor temperature = 26°C.
At 6 PM, the outdoor temp drops to 20°C.
The indoor temperature won’t drop instantly to 20°C – it will gradually decrease.
The lag features help the model learn this delay and predict better.


## Data pre-processing
- Convert timstapms to a time-series format
- Handdle missing values
- Normalize data for better model performance

## Exploratory Data Analysis (EDA)
- Plot temperature trends overtime
- Identify daily patterns (e.g., when the indoor temperature is highest relative to outdoor temperature).

## Model Selection (We will explore time-series models)
- ARIMA (good for capturing trends and seasonality).
- Facebook Prophet (handles irregular data and seasonality well).
- LSTM Neural Networks (deep learning approach for sequential data).

## Model Training & Evaluation
- Train the model on historical data.
- Validate predictions on unseen data.

## Make Predictions
- Forecas optimal ventilations times based on patterns.
- Compare predictions to real-world conditions.


LINKS TO DATA SPREADSHEET

FOTO OF THE GRAPH

