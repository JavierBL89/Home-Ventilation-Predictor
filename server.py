from flask import Flask, request, jsonify, render_template,send_from_directory
import pandas as pd
import numpy as np
from models.arima import optimized_arima_model
from dotenv import load_dotenv
import os

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
    # ✅ Rename 'dt_txt' to 'timestamp' (since OpenWeather sends 'dt_txt')
    df.rename(columns={"dt_txt": "timestamp"}, inplace=True)
    # ✅ Extract temperature (rename it to outdoor_temperature)
    df["outdoor_temperature"] = df["main"].apply(lambda x: x["temp"])

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

   # Predict next 48 hours indoor temperature
    arima_model = optimized_arima_model()
    forecast = arima_model.predict(start=len(df), end=len(df) + 46, dynamic=False)

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
    avg_temp = df["outdoor_temperature"].mean()
    winter_mode = avg_temp < 15  # If the average outdoor temp is below 15°C, assume winter


    # Suggest 2 ventilation periods:
    #### Ensure ventilation avoids extreme cold in winter & extreme heat in summer. 
    #### Pick the best hours within these ranges instead of just one.
    best_hour = None
    best_morning_hour = None
    best_evening_hour = None

    ## Find the absolute best ventilation time (could be night)**
    # Compute temperature difference between forecasted indoor temperature and outdoor temperature
    # Now compute temp difference properly
    temp_diff = (forecast - df["outdoor_temperature"].reindex(forecast.index)).dropna()
    print("Temperature Difference After Dropping NaN:\n", temp_diff)

    # Ensure there's at least one valid value before finding idxmax()
    if not temp_diff.empty:
        if winter_mode:
            # In winter, look for the **smallest difference** (to avoid bringing in very cold air)
            best_hour = temp_diff.idxmin().hour
            print(f"BEST HOUR {best_hour}" )
        else:
            # In summer, go for max cooling
            best_hour = temp_diff.idxmax().hour
    else:
        best_hour = -1  # Use -1 as a fallback instead of a string


    if winter_mode:
        # WINTER - choose the warmest hour of the day
        morning_hours = df.between_time("06:00", "12:00")
        evening_hours = df.between_time("13:00", "18:00")

        best_morning_hour = morning_hours["outdoor_temperature"].idxmax().hour if not morning_hours.empty else None
        best_evening_hour = evening_hours["outdoor_temperature"].idxmax().hour if not evening_hours.empty else None
    else:
        # summer - the best hour for cooling effect (indoor - outdoor max difference)**
        morning_hours = temp_diff.between_time("06:00", "12:00")
        evening_hours = temp_diff.between_time("18:00", "23:00")

        best_morning_hour = morning_hours.idxmin().hour if not morning_hours.empty else None
        best_evening_hour = evening_hours.idxmin().hour if not evening_hours.empty else None

    # Ensure valid output
    best_morning_hour = f"{best_morning_hour}:00" if best_morning_hour is not None else "No optimal morning ventilation"
    best_evening_hour = f"{best_evening_hour}:00" if best_evening_hour is not None else "No optimal evening ventilation"

    print("Available hours for alternative:", temp_diff.index.hour.tolist())

    # 🔥 **Ensure we always suggest 2 alternative options**
    suggested_hours = []

    # Ensure `best_hour` is only added once
    if best_hour is not None and isinstance(best_hour, (int, float)):
        suggested_hours.insert(0, f"{best_hour}:00")

   # Get all alternatives sorted by score (not just time)
    if best_hour != -1:
        alt_sorted = temp_diff.drop(index=forecast.index[forecast.index.hour == best_hour])
    else:
        alt_sorted = temp_diff

    alt_sorted = alt_sorted.sort_values(ascending=winter_mode)  # Min for winter, max for summer
    alt_hours = alt_sorted.index[0].hour if not alt_sorted.empty else None

    print("Filtered alternative hours:", alt_hours)  # Debugging

    if alt_hours is not None:
        suggested_hours.append(f"{alt_hours}:00")
    else:
        print("No alternative hours found, using backup logic")
        # Backup: Pick the next closest hour from forecast if available
        forecast_hours = [h for h in forecast.index.hour if h != best_hour]
        if forecast_hours:
            suggested_hours.append(f"{forecast_hours[0]}:00")
        else:
            suggested_hours.append("No optimal alternative found")

    # Ensure only 2 unique suggested times
    suggested_hours = sorted(list(set(suggested_hours)))[:2]  # Remove duplicates & keep first two and order ascendently

    print("Final suggested hours:", suggested_hours)  # Debugging


    ## More uselful weather data
    weather_condition = weather_data[0]["weather"][0]["main"].lower()  # e.g., "clouds"
    avg_temp = round(df["outdoor_temperature"].mean(), 1)
    max_temp = round(df["outdoor_temperature"].max(), 1)
    min_temp = round(df["outdoor_temperature"].min(), 1)


    return jsonify({
        "bestVentilationTime": f"{best_hour}:00",
        "alternativeTimes": [h for h in suggested_hours if h != f"{best_hour}:00"],
        "morningSuggestion": best_morning_hour,
        "eveningSuggestion": best_evening_hour,
        "season": "winter" if winter_mode else "summer",
        "weatherCondition": weather_condition,
        "avgTemperature": avg_temp,
        "maxTemperature": max_temp,
        "minTemperature": min_temp
   }), 200


if __name__ == '__main__':
    app.run(debug=True)
