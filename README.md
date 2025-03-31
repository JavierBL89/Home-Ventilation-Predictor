# 🏡 Home Ventilation Predictor


📦 How to run the project: [Setup & Execution Guide ➜](/SETUP.md)


This project aims to predict the **optimal hour of the day to ventilate your house** in order to:

- ❄️ **Reduce energy consumption** by minimizing heater or air conditioner usage.
- 🌬️ **Improve indoor air quality** by ventilating during the best thermal exchange periods.
- ♻️ **Align with seasonal logic**, such as ventilating during the warmest hours in winter and the coolest in summer.

> ⚠️ **Note:** This is a very basic prediction that only uses **outdoor and indoor temperature**. It **does not consider** humidity, wind speed, air quality, or other meteorological factors yet.

---

## 🎯 The Goal

We want to determine the most optimal hour in the day to ventilate the house, based on:

- 📉 **Indoor vs. outdoor temperature** differences
- 🌅 **Daily temperature patterns** (e.g., mornings or evenings being cooler)
- ❄️☀️ **Seasonal behavior** (e.g., different ventilation strategies in winter vs. summer)


---

## 🔍 Why Use a Time-Series Model?

When predicting events over time, we can choose between:

### 📈 Regression Models
- Assumes that each input (e.g., temperature, humidity) has a **direct effect** on the output (optimal ventilation time).
- Ignores the **temporal order** of the data (no memory of the past).

### 🕒 Time-Series Models
- Considers the **chronological order** of temperature data.
- Learns from **trends**, **seasonal patterns**, and **lag effects** to make smarter predictions.
- Ideal for our case: temperature varies naturally over time and across seasons.

👉 For this reason, time-series modeling is a **better fit** for this problem.

---

## ⏱️ Time-Series Models Considered

| Model Type | Description |
|------------|-------------|
| **Moving Average / Exponential Smoothing** | Smooths out noise but lacks long-term predictive power. |
| **SARIMAX (Seasonal ARIMA)** | Powerful statistical model that captures both trends and seasonality. |
| **Prophet (by Facebook)** | Great for capturing seasonal patterns and trend shifts automatically. |
| **LSTMs (Deep Learning)** | Neural networks that handle long sequences and learn long-term dependencies. |

## ⏱️ Time-Series Models Implemented
✅ **Prophet (by Facebook)**: [Prophet ➜](/Prophet.md)  
✅**SARIMAX (Seasonal ARIMA)** [SARIMAX Overview ➜](/SARIMAX.md)  
---


### 🔍 Prophet vs SARIMAX – Key Conceptual Differences

| **Aspect**           | **Prophet** ✅                                       | **SARIMAX** ⚙️                                      |
|----------------------|------------------------------------------------------|-----------------------------------------------------|
| **Trend**            | ✅ Automatically detects trend shifts (changepoints) | ⚠️ Assumes trend is linear or needs manual tuning    |
| **Stationarity**     | ✅ Works with non-stationary data                     | ❌ Requires stationary data (ADF test required)       |
| **Seasonality**      | ✅ Built-in (daily, weekly, yearly)                   | ⚠️ Must configure seasonality manually (P,D,Q,s)     |
| **Outliers**         | ✅ Robust to outliers                                 | ❌ Sensitive to outliers                             |
| **Missing Data**     | ✅ Handles missing data and irregular intervals       | ❌ Struggles with missing values                     |
| **Model Type**       | Additive/multiplicative time-series decomposition    | Parametric (AR, I, MA, seasonal)                    |
| **Interpretability** | ✅ Easy to interpret trend/seasonality components     | ⚠️ More technical and parameter-based                |
| **Forecasting Style**| Decomposable model: trend + season + holidays        | Forecasts based on past lags, differencing          |
| **Use Case**         | Best for business cycles with irregular data         | Best for stable, autoregressive time series         |


> 🔸 Prophet learns from trend changes over time, while SARIMAX assumes the same behavior continues into the future unless you transform the data.

### 🔬 In Short:

| **Model**   | **Handles Trend** | **Requires Stationarity** | **Detects Sudden Changes** | **Built-in Seasonality** |
|-------------|-------------------|----------------------------|-----------------------------|---------------------------|
| **SARIMAX** | ⚠️ Limited         | ✅ Yes                     | ❌ No                       | ⚠️ Manual setup required  |
| **Prophet** | ✅ Yes             | ❌ No                      | ✅ Yes                      | ✅ Yes                    |


On paper, Prophet looks like a dream for time series forecasting,

But the trade-off is:

Prophet makes bigger assumptions under the hood, so it might overfit or smooth too much for short-term or highly erratic signals.

ARIMA can still outperform Prophet on well-behaved, short-range data that’s been properly preprocessed.


## 🧰 Frameworks & Libraries Used

- `pandas` – Data manipulation
- `numpy` – Numerical calculations
- `matplotlib` / `seaborn` – Visualization
- `scikit-learn` – Evaluation metrics
- `statsmodels` – SARIMAX model
- `prophet` – Facebook’s time-series forecaster
- `tensorflow` – Used for potential LSTM model integration
- `transformers` – Reserved for future integration of NLP-based enhancements

---

## SARIMAX View

![SARIMAX View](images/SARIMAX.png)
![Prophet View](images/Prophet.png)