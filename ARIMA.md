ARIMA (AutoRegressive Integrated Moving Average) is a statistical model that predicts future values based on past observations.
It is useful for **time-series forecasting** because it accounts for **trends, seasonability, and lag effects.**


* Arima is based on past values
* If the data has **trends**, **ARIMA assumes they will continue forever** (which isn't always true)
* Making the data stacionary removes misleading patterns and allow ARIMA **to focus on short-term relationships**

## What is Stattionary?

A time series is stationary if:

1. Its mean, variance, and autocorrelation stay constant over time
2. It does not have a long-term trend (e.g., a rising/falling pattern).
3. Statistical properties don't change over time.

A time series is non-stationary if:

1. It has a **clear trend**(e.g., increasing temperatures over time).
2. Its **mean or variance** changes over time.
3. It has seasonal patterns that repreat periodically.

## Understanding the Augmented Dickey-Fuller (ADF) Test

ARIMA works with Stationary data, and the **ADF test checks whether a time series is stationary or non-stationary.**

The ADF test helps check if our data is stationary or non-stationary.
It gives two important values:

1. **ADF Statistic** → A number that helps determine stationarity.
2. **p-value** → The probability that the data is non-stationary.

####  How to Interpret the p-value?
* p-value < 0.05 → ✅ The data is stationary. → We can use ARIMA without modification.
* p-value > 0.05 → ❌ The data is non-stationary. → We need to make it stationary before using ARIMA.


**If the Data is Non-Stationary**
If p-value > 0.05, we can differentiate the data:
```
  df["indoor_temperature_diff"] = df["indoor_temperature"].diff().dropna()
  # This calculates the change between consecutive values, removing trends and making the series stationary.
```

After differencing, we re-run the ADF test:
```
  result = adfuller(df["indoor_temperature_diff"].dropna())

  print("ADF Statistic after differencing:", result[0])
  print("p-value after differencing:", result[1])
  If p-value < 0.05 now, the data is stationary, and we can use ARIMA.
```


### Our Model Results

- First run 
    ADF Statistic: -1.9039103900954981
    p-value: 0.330223781871717

-> Since p-value < 0.05, the data is not-stationary, meaning we need to apply differencing


- After applying differencing

ADF Statistic: -36.28038086091116
p-value: 0.0

-> Since p-value = 0.0 (< 0.05), the data is now stationary, meaning we can proceed with ARIMA



## Loading data

dataLoader.py

```
    import pandas as pd
    # Load dataset
    df = pd.read_csv("madrid_fake_temperature_data_with_lags.csv")

    # Convert timestamp column to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Set the timestamp as the index (required for ARIMA)
    df.set_index("timestamp", inplace=True)
```

## Train the ARIMA Model

```
from statsmodels.tsa.arima.model import ARIMA

# TRAIN arima with the stationary data
model = ARIMA(df["indoor_temperature_diff"].dropna(), order=(5,1,0)) # (p,d.q)
model_fit = model.fit()

# model summary
print(model_fit.summary())
```
Explanation of ARIMA (5,1,0):

p = 5 → Uses 5 past values (lags) for prediction.
d = 1 → Data was differenced once to make it stationary.
q = 0 → No moving average component.

##### Models' summary output


                                 SARIMAX Results                                  
===================================================================================
Dep. Variable:     indoor_temperature_diff   No. Observations:                 8735
Model:                      ARIMA(5, 1, 0)   Log Likelihood              -10300.001
Date:                     Fri, 07 Mar 2025   AIC                          20612.003
Time:                             17:04:21   BIC                          20654.453
Sample:                         01-02-2024   HQIC                         20626.469
                              - 12-30-2024                                         
Covariance Type:                       opg                                         
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
ar.L1         -1.3264      0.009   -145.155      0.000      -1.344      -1.308
ar.L2         -1.2737      0.014    -89.615      0.000      -1.302      -1.246
ar.L3         -1.0015      0.016    -63.068      0.000      -1.033      -0.970
ar.L4         -0.6178      0.014    -44.002      0.000      -0.645      -0.590
ar.L5         -0.2494      0.009    -26.641      0.000      -0.268      -0.231
sigma2         0.6191      0.006     96.654      0.000       0.607       0.632
===================================================================================
Ljung-Box (L1) (Q):                  25.01   Jarque-Bera (JB):              2026.86
Prob(Q):                              0.00   Prob(JB):                         0.00
Heteroskedasticity (H):               1.08   Skew:                             0.07
Prob(H) (two-sided):                  0.03   Kurtosis:                         5.36
===================================================================================

Warnings:
[1] Covariance matrix calculated using the outer product of gradients (complex-step).


#### How to Interpret the ARIMA Model Output

ARIMA model summary includes important metrics that help us understand how well it fits the data.
 Here's what to focus on:

### **How to Interpret the ARIMA Model Output**  

Your ARIMA model summary includes **important metrics** that help us understand how well it fits the data. Here's what to focus on:

---

##### **1️⃣ Model Selection Criteria**
| **Metric** | **What It Means** | **What to Look For** |
|------------|------------------|----------------------|
| **AIC (Akaike Information Criterion)** | Measures model quality (lower is better). | Compare with other models; lower AIC = better fit. |
| **BIC (Bayesian Information Criterion)** | Similar to AIC but penalizes complexity more. | Lower is better. |
| **Log Likelihood** | Measures how well the model explains the data. | Higher (less negative) means better fit. |

🔹 **Model values**:
- **AIC = 20612** → Lower is better.
- **BIC = 20654** → Compare with other models.
- **Log Likelihood = -10300** → Compare with other models.

---

##### **2️⃣ Coefficients (AR Terms)**
| **Term** | **Value** | **Interpretation** |
|------------|----------|--------------------|
| **ar.L1 = -1.3264** | Strong negative correlation with 1-hour lag. |
| **ar.L2 = -1.2737** | 2-hour lag still has a strong effect. |
| **ar.L3 = -1.0015** | 3-hour lag affects predictions. |
| **ar.L4 = -0.6178** | 4-hour lag has a moderate effect. |
| **ar.L5 = -0.2494** | 5-hour lag has a small effect. |

🔹 **Interpretation**:  
- All AR terms are **statistically significant** (p-value = 0.000).  
- Negative values indicate **reverting behavior**—a **decrease in past values tends to be followed by an increase**.  
- The **first few lags have the highest influence**, meaning past temperatures (up to 3 hours ago) are **very important** for predicting current values.

---

### **3️⃣ Residuals & Model Fit**
| **Metric** | **What It Means** | **Your Value** |
|------------|------------------|---------------|
| **Ljung-Box Test (Q)** | Checks if residuals are random (high values mean poor fit). | **Q = 25.01** (low = good) |
| **Jarque-Bera (JB) Test** | Checks if errors follow a normal distribution. | **JB = 2026.86** (p < 0.05 → not normal) |
| **Kurtosis** | Measures tail behavior (should be near 3). | **5.36 (high)** (indicates heavier tails) |
| **Skew** | Measures asymmetry (should be near 0). | **0.07 (close to normal)** |

🔹 **Interpretation**:
- **Ljung-Box Test:** Residuals appear **random**, meaning the model captures most of the patterns. ✅  
- **Jarque-Bera Test:** Residuals are **not normally distributed** (but this is common for real-world data).  
- **Kurtosis is high** → The model sometimes produces extreme predictions (rare events).  
- **Skew is low** → Errors are mostly symmetric, which is good.

---

### **4️⃣ Model Noise (Sigma²)**
- **Sigma² (0.6191)** → This is the variance of the residuals (errors).  
- **Lower values = more stable model** (values < 1 are generally good). ✅

---

## **🔹 Summary: Is This a Good ARIMA Model?**
✅ **Strengths:**
- The model **explains past data well** (low AIC/BIC, strong AR terms).
- Residuals **appear random** (Ljung-Box test is fine).
- **Sigma² is low**, meaning stable predictions.

⚠️ **Potential Issues:**
- Residuals **are not normally distributed** (JB test).
- **High kurtosis** → Possible extreme predictions.

---

## **🔹 Next Steps**
1️⃣ **Run Forecasting:**

```python
df["arima_forecast"] = model_fit.predict(start=len(df)-100, end=len(df)-1, dynamic=False)

# Plot results
import matplotlib.pyplot as plt
plt.figure(figsize=(12,6))
plt.plot(df.index[-500:], df["indoor_temperature"][-500:], label="Actual Indoor Temp")
plt.plot(df.index[-100:], df["arima_forecast"], label="ARIMA Forecast", color="red")
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("ARIMA Forecasting for Indoor Temperature")
plt.legend()
plt.show()
```
2️⃣ **Evaluate Accuracy:**  
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(df["indoor_temperature"][-100:], df["arima_forecast"].dropna())
mse = mean_squared_error(df["indoor_temperature"][-100:], df["arima_forecast"].dropna())

print("Mean Absolute Error (MAE):", mae)
print("Mean Squared Error (MSE):", mse)
```

**Models' first results**
Mean Absolute Error (MAE): 6.201658053108511 
Mean Squared Error (MSE): 38.770074835694174

 - Mean Absolute Error (MAE) = 6.20
On average, ARIMA's predictions are 6.2°C off from the actual indoor temperature.
Lower MAE is better (closer to 0 means more accurate predictions).

 -  Mean Squared Error (MSE) = 38.77
This penalizes larger errors more than MAE.
A lower MSE is better, but it’s harder to interpret because it's squared.


# 🔹 Is This a Good ARIMA Model?

✅ Strengths:

- The model captures trends in temperature changes.
- AR terms (lags) show past temperatures influence the present.

⚠️ Weaknesses:

- MAE = 6.2°C is quite high, meaning ARIMA’s predictions aren’t very close.
- ARIMA struggles with long-term dependencies like seasonality (summer vs winter).


## Improving the model

1. **Optimize** (p,d,q) using **Auto-ARIMA**

Instead of manuallly choosing (5,1,0), let’s let Python find the best parameters:

Find the best (p, d, q) values automatically
```python
from pmdarima import auto_arima
auto_model = auto_arima(df["indoor_temperature"], 
                        seasonal=False, 
                        stepwise=True, 
                        trace=True)

# Print the best parameters
print(auto_model.order)

Output: 
    Best model:  ARIMA(0,1,1)(0,0,0)[0]          
    Total fit time: 8.053 seconds
    (0, 1, 1)
```
**Models first results**
Mean Absolute Error (MAE): 0.44353527306546797
Mean Squared Error (MSE): 0.29745561383783964

 - Mean Absolute Error (MAE) dropped from 6.2°C to 0.44°C → Your ARIMA predictions are now much closer to actual values!
 - Mean Squared Error (MSE) dropped from 38.77 to 0.29 → The model makes significantly fewer large mistakes.


2. **Try Seasonal ARIMA (SARIMA)**
Since indoor temperatures follow daily and seasonal patterns, we can use SARIMA, which extends ARIMA by adding seasonal components.

```python

from statsmodels.tsa.statespace.sarimax import SARIMAX

# Train a Seasonal ARIMA model with 24-hour seasonality
sarima_model = SARIMAX(df["indoor_temperature"], 
                       order=auto_model.order,  # Best (p,d,q) from auto_arima
                       seasonal_order=(1, 1, 1, 24))  # Seasonal (P,D,Q,24 hours)
sarima_fit = sarima_model.fit()
```
**NOTE**: This enhancement Introduced complexity and noise which made the model more inacurate with higher error values.


### **Final Thoughts**
🔹 **Your model is performing well** and captures **past trends effectively**.  
🔹 If you want to improve it, we can **tune p, d, q parameters** or **check residuals visually**.  
🔹 If ARIMA’s predictions look good, we can move on to **Prophet for comparison**.


## -> Next Step: Compare ARIMA with Prophet
Prophet is better for seasonal trends and might improve prediction accuracy.
