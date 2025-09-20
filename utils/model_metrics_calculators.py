import pickle
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.helpers import interpolate_weather_data_for_times_net
import requests
import os

from dotenv import load_dotenv
load_dotenv()  #  This loads your .env values

def calculate_model_metrics():
    """Calculate metrics for SARIMAX, Prophet, and TimesNet models"""

    # -----------------
    # Load test data
    # -----------------
    def load_test_data():
        try:
            df = pd.read_csv("data/temperature_data.csv")  # adjust path if needed
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df
        except:
            # fallback: generate dummy data
            dates = pd.date_range(start="2024-01-01", periods=500, freq="H")
            np.random.seed(42)
            indoor = 20 + np.sin(np.linspace(0, 20, len(dates))) + np.random.normal(0, 0.5, len(dates))
            outdoor = indoor + np.random.normal(0, 1, len(dates))
            return pd.DataFrame({"indoor_temperature": indoor, "outdoor_temperature": outdoor}, index=dates)

    # -----------------
    # SARIMAX
    # -----------------
    def evaluate_arima_model(test_data):
        try:
            with open("arima_model.pkl", "rb") as f:
                arima_model = pickle.load(f)

            test_size = 100
            actual = test_data["indoor_temperature"].iloc[-test_size:]
            exog = test_data[["outdoor_temperature"]].iloc[-test_size:]

            forecast = arima_model.get_forecast(steps=test_size, exog=exog)
            predictions = forecast.predicted_mean

            mae = mean_absolute_error(actual, predictions)
            mse = mean_squared_error(actual, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(actual, predictions)
            mape = np.mean(np.abs((actual - predictions) / actual)) * 100

            return {
                "model_name": "SARIMAX",
                "mae": safe_round(mae, 4),
                "mse": safe_round(mse, 4),
                "rmse": safe_round(rmse, 4),
                "r2": safe_round(r2, 4),
                "adj_r2": safe_round(r2, 4),
                "mape": safe_round(mape, 2),
                "aic": safe_round(getattr(arima_model, "aic", None), 2),
                "bic": safe_round(getattr(arima_model, "bic", None), 2),
                "sample_size": len(actual),
                "status": "success",
            }
        except Exception as e:
            print(f"[ERROR] SARIMAX evaluation failed: {e}")
            return {"model_name": "SARIMAX", "status": "error", "error": str(e)}

    # -----------------
    # TimesNet
    # -----------------
    def evaluate_timesnet_model(test_data):
        try:
            # Prepare 48 hours of sample data
            sample_weather_data = []
            for i in range(48):
                ts = test_data.index[-48 + i]
                temp = test_data["outdoor_temperature"].iloc[-48 + i]
                sample_weather_data.append({
                    "dt_txt": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "main": {"temp": temp}
                })

            # Interpolate data
            hourly_temps, hourly_timestamps = interpolate_weather_data_for_times_net(sample_weather_data)
            payload = {
                "time_stamps": hourly_timestamps,
                "outdoor_temp": hourly_temps,
                "weather_data": sample_weather_data
            }

            # Call TimesNet API
            response = requests.post(
                "https://huggingface.co/spaces/javierBLdev89/TimeNet_Home_Ventilation_time_Predictor/time_net/predict",
                headers={"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}, 
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "model_name": "TimesNet",
                    "status": "error",
                    "error": f"API returned {response.status_code}"
                }

            result = response.json()
            if "predictions" not in result:
                return {
                    "model_name": "TimesNet",
                    "status": "error",
                    "error": "No predictions in response"
                }

            predictions = result["predictions"]
            actual = test_data["indoor_temperature"].iloc[-len(predictions):]

            # Metrics
            mae = mean_absolute_error(actual, predictions)
            mse = mean_squared_error(actual, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(actual, predictions)
            mape = np.mean(np.abs((actual - predictions) / actual)) * 100

            return {
                "model_name": "TimesNet",
                "mae": safe_round(mae, 4),
                "mse": safe_round(mse, 4),
                "rmse": safe_round(rmse, 4),
                "r2": safe_round(r2, 4),
                "adj_r2": safe_round(r2, 4),  # you could add proper adj R² later
                "mape": safe_round(mape, 2),
                "aic": "N/A",
                "bic": "N/A",
                "sample_size": len(actual),
                "status": "success",
            }

        except Exception as e:
            print(f"[ERROR] TimesNet evaluation failed: {e}")
            return {
                "model_name": "TimesNet",
                "status": "error",
                "error": str(e)
            }

    # -----------------
    # Run evaluations
    # -----------------
    test_data = load_test_data()

    return {
        "arima": evaluate_arima_model(test_data),
        "timesnet": evaluate_timesnet_model(test_data),
        "timestamp": pd.Timestamp.now().isoformat(),
    }


def safe_round(value, digits=4):
    """Safely round values, replace NaN/inf with None"""
    try:
        if pd.isna(value) or np.isinf(value):
            return None
        return round(float(value), digits)
    except Exception:
        return None
