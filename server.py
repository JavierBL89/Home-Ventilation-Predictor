from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import numpy as np
from utils.helpers import get_best_hour_by_season, get_season_from_date, interpolate_weather_data_for_times_net
from utils.predict_best_hours import predict_best_hours
from dotenv import load_dotenv
import os
import requests
from flask_cors import CORS
import pickle
from utils.model_metrics_calculators import calculate_model_metrics

from dotenv import load_dotenv
load_dotenv()  # ⬅️ This loads your .env values


app = Flask(__name__, static_folder="static", template_folder='templates')
CORS(app, origins=["https://home-ventilation-predictor.onrender.com", "http://http://127.0.0.1:5001/"])


# Serve static files like images
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


@app.route('/', methods=['GET'])
def home_page():
    """API endpoint to render HOME PAGE"""
    return render_template('index.html') 


@app.route('/metrics', methods=['GET'])
def metrics_page():
    """API endpoint to render MODEL METRICS PAGE"""
    return render_template('metrics.html')  # Create this template


@app.route("/config")
def get_config():
    return {"openWeatherAPI": os.environ.get("OPENWEATHER_API_KEY", "")}


# NEW METRICS ENDPOINTS
@app.route('/api/model_metrics', methods=['GET'])
def get_model_metrics():
    try:
        metrics = calculate_model_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'arima': {'status': 'error', 'error': str(e)},
            'prophet': {'status': 'error', 'error': str(e)},
            'timesnet': {'status': 'error', 'error': str(e)}
        }), 500


@app.route('/api/model_metrics/<model_name>', methods=['GET'])
def get_single_model_metrics(model_name):
    """API endpoint to get metrics for a specific model"""
    try:
        all_metrics = calculate_model_metrics()
        
        if model_name.lower() in ['arima', 'sarimax']:
            return jsonify(all_metrics['arima'])
        elif model_name.lower() in ['timesnet', 'timesnet']:
            return jsonify(all_metrics['timesnet'])
        else:
            return jsonify({'error': f'Unknown model: {model_name}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/process_weather', methods=['POST'])
def predict():
    """API endpoint to get ventilation time based on current weather data."""
   
    data = request.get_json()
    if not data or "weatherData" not in data or "targetDate" not in data:
        return jsonify({"error": "Invalid request"}), 400

    model = data.get("model", "").lower()
    print(f"🔧 Requested model: {model}")
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
        with open("arima_model.pkl", "rb") as f:
            arima_model = pickle.load(f)
        forecast_values = arima_model.predict(start=len(df), end=len(df) + 47, dynamic=False)
        forecast = pd.Series(forecast_values)
    elif data["model"] == "timesNet":
        # 1.Interpolate data for a full 48h data entries 
        hourly_temps, hourly_timestamps = interpolate_weather_data_for_times_net(weather_data)
        payload = {
            "time_stamps": hourly_timestamps,
            "outdoor_temp": hourly_temps,
            "weather_data": weather_data
        }
        # Step 3: Send POST request to your Hugging Face Space
        response = requests.post(
                     #"http://192.168.1.100/time_net/predict",
                    "https://javierBLdev89-TimeNet-Home-Ventilation-time-Predictor.hf.space/time_net/predict",
                    #"https://api-inference.huggingface.co/models/javierBLdev89/TimeNet-Home-Ventilation-time-Predictor",
                     headers={"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}, 
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
        return jsonify({"error": f"Unknown model '{model}'"}), 400
            
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

    season = get_season_from_date(selected_date)
    best_hours_prediction = predict_best_hours(df, weather_data, season, forecast)
    
    return best_hours_prediction

port = 0
if get_config() == True:
    port = 3000
else:
    port = 5001

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", port)), debug=True)