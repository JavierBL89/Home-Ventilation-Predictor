#from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA

from dataLoader import data_loader

df = data_loader()

# This removes the long-term trend and makes the data more stable.
df["indoor_temperature_diff"] = df["indoor_temperature"].diff().dropna()

# Set the timestamp as the index (required for ARIMA)
df.set_index("timestamp", inplace=True)

#### Perform Augmented Dickey-Fuller (ADF) test on differenced data
#result = adfuller(df["indoor_temperature_diff"].dropna())
#### Print the test result
#print("ADF Statistic:", result[0])
#print("p-value:", result[1])



########## ARIMA MODEL #########

# Train ARIMA on the stationary data
model = ARIMA(df["indoor_temperature_diff"].dropna(), order=(5,1,0))  # (p,d,q)
model_fit = model.fit()

# Print the model summary
#print(model_fit.summary())

##### FORECASTING
df["arima_forecast"] = model_fit.predict(start=len(df)-100, end=len(df)-1, dynamic=False)

# plot results (plotting the actual indoor temperature and ARIMA's forecast to visually compare them)
import matplotlib.pyplot as plt

plt.figure(figsize=(12,6)) #Creates a new figure (graph) with a size of 12x6 inches.
plt.plot(df.index[-500:], df["indoor_temperature"].iloc[-500:], label="Actual Indoor Temp")
plt.plot(df.index[-100:], df["arima_forecast"].iloc[-100:], label="ARIMA Forecast", color="red")
plt.xlabel("Date")
plt.ylabel("Temperature (Cº)")
plt.title("ARIMA Forecasting for Indoor Temperature")
plt.legend()
# plt.show() # 👈 This ensures the graph is displayed if using terminal and not Jupyter Notebook



##### EVALUATE ACCURACY (1st Attempt)
from sklearn.metrics import mean_absolute_error, mean_squared_error

mae = mean_absolute_error(df["indoor_temperature"][-99:], df["arima_forecast"].dropna())
mse = mean_squared_error(df["indoor_temperature"][-99:], df["arima_forecast"].dropna())
print("")
print("EVALUATE ACCURACY (1st Attempt)")
print("Mean Absolute Error (MAE):", mae)
print("Mean Squared Error (MSE):", mse)


##### IMPROVING ARIMA (optimize p,d,q)
from pmdarima import auto_arima

# find the best (p, d, q) values automatically
auto_model = auto_arima(df["indoor_temperature"], seasonal=False, stepwise=True,trace=True)
### Print the best parameters
#print(auto_model.order)

# Use the optimized order from auto_arima
best_p, best_d, best_q = auto_model.order  

# Train ARIMA
model = ARIMA(df["indoor_temperature"], order=(best_p, best_d, best_q))
model_fit = model.fit()

# Forecast
df["arima_forecast"] = model_fit.predict(start=len(df)-100, end=len(df)-1, dynamic=False)

plt.figure(figsize=(12,6)) #Creates a new figure (graph) with a size of 12x6 inches.
plt.plot(df.index[-500:], df["indoor_temperature"].iloc[-500:], label="Actual Indoor Temp")
plt.plot(df.index[-100:], df["arima_forecast"].iloc[-100:], label="ARIMA Forecast", color="red")
plt.xlabel("Date")
plt.ylabel("Temperature (Cº)")
plt.title("ARIMA Forecasting for Indoor Temperature")
plt.legend()
# plt.show() # 👈 This ensures the graph is displayed if using terminal and not Jupyter Notebook


##### EVALUATE ACCURACY (2st Attempt)
mae = mean_absolute_error(df["indoor_temperature"][-100:], df["arima_forecast"].dropna())
mse = mean_squared_error(df["indoor_temperature"][-100:], df["arima_forecast"].dropna())
print("")
print("EVALUATE ACCURACY (2nd Attempt)")
print("Mean Absolute Error (MAE):", mae)
print("Mean Squared Error (MSE):", mse)
