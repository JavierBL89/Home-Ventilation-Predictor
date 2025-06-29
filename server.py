from flask import Flask, request, jsonify, render_template,send_from_directory
import pandas as pd
import numpy as np
from models.arima import optimized_arima_model
from models.prophet import prophet_model,simulate_indoor_temperature
from utils.helpers import get_best_hour_by_season, get_season_from_date, interpolate_weather_data_for_times_net
from utils.predict_best_hours import predict_best_hours
from dotenv import load_dotenv
import os
import requests



load_dotenv()  # Load .env file
app = Flask(__name__, static_folder="static", template_folder='templates')

# Serve static files like images
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)



@app.route('/', methods=['GET'])
def home_page():
    """API endpoint to to render HOME PAGE"""
    return render_template('index.html') 


@app.route("/config")
def get_config():
    return jsonify({"openWeatherAPI": os.getenv("OPENWEATHER_API_KEY")})


@app.route('/process_weather', methods=['POST'])
def predict():
    """API endpoint to get ventilation time based on current weather data."""

    data = request.get_json()
    if not data or "weatherData" not in data or "targetDate" not in data:
        return jsonify({"error": "Invalid request"}), 400

    weather_data = data["weatherData"]
    selected_date = data["targetDate"]
    print("Received Weather Data:", weather_data)  # Debugging

    # convert weather data into a Dataframe
    df = pd.DataFrame(weather_data)
    df.rename(columns={"dt_txt": "timestamp"}, inplace=True) # Rename 'dt_txt' to 'timestamp' (since OpenWeather sends 'dt_txt')
    df["outdoor_temperature"] = df["main"].apply(lambda x: x["temp"]) # Extract temperature (rename it to outdoor_temperature)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    
    # Determine the Model to be used
    if data["model"] == "sarimax":
        # Predict next 48 hours indoor temperature
        arima_model = optimized_arima_model()
        forecast = arima_model.predict(start=len(df), end=len(df) + 46, dynamic=False)

    if data["model"] == "timesNet":
        # 1.Interpolate data for a full 48h data entries 
        hourly_temps, hourly_timestamps = interpolate_weather_data_for_times_net(weather_data)
        payload = {
            "time_stamps": hourly_timestamps,
            "outdoor_temp": hourly_temps,
            "weather_data": weather_data
        }
        # Step 3: Send POST request to your Hugging Face Space
        response = requests.post(
                    "https://javierBLdev89-TimeNet-Home-Ventilation-time-Predictor.hf.space/time_net/predict", 
                    json=payload
                )
        # Check response
        if response.status_code == 200:
            result = response.json()
            print("✅ TimeNet Forecast Response:", result)
            return jsonify(result), 200
        else:
            print("❌ Failed to get TimeNet Forecast:", response.text)
            return jsonify({"error": "Failed to get TimeNet forecast"}), 500

    else:
       df["indoor_temperature"] = simulate_indoor_temperature(df)  # or however you calculate this
       forecast = prophet_model(df)

   # Ensure outdoor temperature column has no missing values
    df["outdoor_temperature"] = df["outdoor_temperature"].interpolate(method="linear")

   # Ensure forecast starts at 00:00 of the selected day
    start_time = pd.Timestamp(selected_date).normalize()  # Normalize to 00:00
    forecast.index = pd.date_range(start=start_time, periods=len(forecast), freq="h")

    # Ensure outdoor temperature has values for all forecast timestamps
    df = df.reindex(forecast.index, method="nearest")  # Use nearest matching values to fill missing timestamps

    print("Forecast:\n", forecast.head(22))
    print("Forecast Index:\n", forecast.index)
    print("Outdoor Temperature:\n", df["outdoor_temperature"].head(22))

    # Determine Winter or summer modo based on today's average temperature
    #avg_temp = df["outdoor_temperature"].mean()
    #winter_mode = avg_temp < 15  # If the average outdoor temp is below 15°C, assume winter

    season = get_season_from_date(selected_date)
    best_hours_prediction = predict_best_hours(df,weather_data,season, forecast)
    
    return best_hours_prediction


if __name__ == '__main__':
    app.run(debug=True)

