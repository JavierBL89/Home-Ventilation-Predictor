#from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import os,sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.dataLoader import data_loader
import pickle



def arima_data_loader():

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
    return df


########## ARIMA MODELs #########

def first_arima_model():

    df=arima_data_loader()
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




def optimized_arima_model():  
        
    ##### IMPROVING ARIMA (optimize p,d,q)     
    from pmdarima import auto_arima     
    from statsmodels.tsa.statespace.sarimax import SARIMAX      
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    import numpy as np

    # disable interactive plotting and use a non-GUI backend:     
    import matplotlib     
    matplotlib.use("Agg")  # Use a non-interactive backend (Agg)     
    import matplotlib.pyplot as plt       

    df = arima_data_loader()
    
    # find the best (p, d, q) values automatically     
    auto_model = auto_arima(df["indoor_temperature"], seasonal=False, stepwise=True, trace=True)
    
    # Use the optimized order from auto_arima(Auto-detect best (p, d, q))     
    best_p, best_d, best_q = auto_model.order        

    # Train ARIMA     
    model = SARIMAX(df["indoor_temperature"], order=(best_p, best_d, best_q), exog=df[["outdoor_temperature"]])  # Include outdoor temp as external regressor      

    model_fit_optimized = model.fit()      

    # Forecast     
    future_exog = df[["outdoor_temperature"]].iloc[-100:]  # Get last 100 exog values     
    df["arima_forecast"] = model_fit_optimized.predict(start=len(df)-100, end=len(df)-1, exog=future_exog)      

    plt.figure(figsize=(12,6)) #Creates a new figure (graph) with a size of 12x6 inches.     
    plt.plot(df.index[-500:], df["indoor_temperature"].iloc[-500:], label="Actual Indoor Temp")     
    plt.plot(df.index[-100:], df["arima_forecast"].iloc[-100:], label="ARIMA Forecast", color="red")     
    plt.xlabel("Date")     
    plt.ylabel("Temperature (Cº)")     
    plt.title("ARIMA Forecasting for Indoor Temperature")     
    plt.legend()     

    ##### EVALUATE ACCURACY WITH FULL METRICS
    actual_values = df["indoor_temperature"].iloc[-100:]     
    predicted_values = df["arima_forecast"].dropna().iloc[-100:]      

    min_length = min(len(actual_values), len(predicted_values))     
    actual_values = actual_values.iloc[-min_length:]     
    predicted_values = predicted_values.iloc[-min_length:]      

    # Calculate all metrics
    mae = mean_absolute_error(actual_values, predicted_values)     
    mse = mean_squared_error(actual_values, predicted_values)
    rmse = np.sqrt(mse)
    r2 = r2_score(actual_values, predicted_values)
    
    # Calculate additional useful metrics
    mape = np.mean(np.abs((actual_values - predicted_values) / actual_values)) * 100  # Mean Absolute Percentage Error
    n = len(actual_values)
    p = len([best_p, best_d, best_q])  # number of parameters
    aic = model_fit_optimized.aic
    bic = model_fit_optimized.bic
    
    # Adjusted R²
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else r2

    print("")     
    print("EVALUATE ACCURACY - COMPREHENSIVE METRICS")     
    print("=" * 50)
    print(f"Mean Absolute Error (MAE): {mae:.4f}")     
    print(f"Mean Squared Error (MSE): {mse:.4f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.4f}")
    print(f"R² Score: {r2:.4f}")
    print(f"Adjusted R² Score: {adj_r2:.4f}")
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
    print(f"AIC: {aic:.2f}")
    print(f"BIC: {bic:.2f}")
    print(f"Model Order (p,d,q): ({best_p}, {best_d}, {best_q})")
    
    # Create metrics dictionary for easy access
    metrics = {
        'mae': round(mae, 4),
        'mse': round(mse, 4),
        'rmse': round(rmse, 4),
        'r2': round(r2, 4),
        'adj_r2': round(adj_r2, 4),
        'mape': round(mape, 2),
        'aic': round(aic, 2),
        'bic': round(bic, 2),
        'model_order': f"({best_p}, {best_d}, {best_q})",
        'sample_size': n
    }

    with open("arima_model.pkl", "wb") as f:         
        pickle.dump(model_fit_optimized, f)      

    return model_fit_optimized, metrics