from flask import Flask, request, jsonify, render_template,send_from_directory
import pandas as pd
import numpy as np
from models.arima import optimized_arima_model
from dotenv import load_dotenv
import os
from datetime import datetime


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
    df.rename(columns={"dt_txt": "timestamp"}, inplace=True) # ✅ Rename 'dt_txt' to 'timestamp' (since OpenWeather sends 'dt_txt')
    df["outdoor_temperature"] = df["main"].apply(lambda x: x["temp"]) # ✅ Extract temperature (rename it to outdoor_temperature)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)
    
    # Determine the Model to be used
    if data["model"] == "sarimax":
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
    #avg_temp = df["outdoor_temperature"].mean()
    #winter_mode = avg_temp < 15  # If the average outdoor temp is below 15°C, assume winter

    season = get_season_from_date(selected_date)


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
        if season == "winter":
            # Avoid freezing ventilation – pick time with smallest difference (least heat loss)
            best_hour = temp_diff.idxmin().hour
        else:
            # Max cooling effect – largest difference
            best_hour = temp_diff.idxmax().hour
    else:
        best_hour = -1  # Only use fallback if no data  

    if season == "winter":
        # Suggest warmest hours
        morning_hours = df.between_time("08:00", "12:00")
        evening_hours = df.between_time("13:00", "17:00")

        best_morning_hour = morning_hours["outdoor_temperature"].idxmax().hour if not morning_hours.empty else None
        best_evening_hour = evening_hours["outdoor_temperature"].idxmax().hour if not evening_hours.empty else None

    elif season == "summer":
        # Suggest coolest (max cooling effect)
        morning_hours = temp_diff.between_time("06:00", "11:00")
        evening_hours = temp_diff.between_time("19:00", "22:00")

        best_morning_hour = morning_hours.idxmin().hour if not morning_hours.empty else None
        best_evening_hour = evening_hours.idxmin().hour if not evening_hours.empty else None

    else:
        # Spring or Autumn – pick most balanced
        morning_hours = temp_diff.between_time("07:00", "12:00")
        evening_hours = temp_diff.between_time("16:00", "20:00")

        best_morning_hour = (morning_hours - morning_hours.median()).abs().idxmin().hour if not morning_hours.empty else None
        best_evening_hour = (evening_hours - evening_hours.median()).abs().idxmin().hour if not evening_hours.empty else None

    # Ensure valid output
    best_morning_hour = f"{best_morning_hour}:00" if best_morning_hour is not None else "No optimal morning ventilation"
    best_evening_hour = f"{best_evening_hour}:00" if best_evening_hour is not None else "No optimal evening ventilation"

    print("Available hours for alternative:", temp_diff.index.hour.tolist())


    suggested_hours = [] # 🔥 **Ensure we always suggest 2 alternative options**
    alt_sorted = temp_diff.copy() # Ensure alt_sorted is always defined

    # Ensure `best_hour` is only added once
    if best_hour is not None and isinstance(best_hour, (int, float)):
        suggested_hours.insert(0, f"{best_hour}:00")

    # Remove best_hour from alternatives
    if best_hour != -1:
        alt_sorted = temp_diff.drop(index=forecast.index[forecast.index.hour == best_hour])
    else:
        alt_sorted = temp_diff

    # 🧠 Apply season-aware filtering to alt_sorted
    if season == "winter":
        alt_sorted = alt_sorted.between_time("04:00", "23:00")
    elif season == "summer":
        alt_sorted = alt_sorted.between_time("06:00", "22:00")
    else:  # spring or autumn
        alt_sorted = alt_sorted.between_time("07:00", "21:00")

    # Then sort depending on whether you want to cool or warm the house
    alt_sorted = alt_sorted.sort_values(ascending=(season == "winter"))  # ascending = True for winter

    # Select alternative hour
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

    top_score = alt_sorted.iloc[0]
    threshold = 1.0 if season in ["spring", "autumn"] else 0.5
    suggested_hours = alt_sorted[abs(alt_sorted - top_score) <= threshold].index.hour.tolist()
    ## suggest alterntive hours
    suggested_hours = [f"{h}:00" for h in sorted(set(suggested_hours))]


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
        "season": season,
        "weatherCondition": weather_condition,
        "avgTemperature": avg_temp,
        "maxTemperature": max_temp,
        "minTemperature": min_temp
   }), 200


def get_best_hour_by_season(temp_diff, df, season):
    if season == "winter":
        # Pick hour with smallest difference (warmest)
        valid_hours = temp_diff.between_time("11:00", "17:00")
        return valid_hours.idxmin().hour if not valid_hours.empty else None

    elif season == "summer":
        # Pick hour with largest cooling effect
        return temp_diff.idxmax().hour if not temp_diff.empty else None

    elif season in ["spring", "autumn"]:
        # Avoid night ventilation, pick reasonable hours
        valid_hours = temp_diff.between_time("06:00", "21:00")
        return valid_hours.idxmax().hour if not valid_hours.empty else None

    # fallback
    return temp_diff.idxmax().hour if not temp_diff.empty else None


# Funtion figures ot the Season category from the target date
def get_season_from_date(date_str):
    # Convert string to datetime object
    date = datetime.strptime(date_str, "%Y-%m-%d")
    month = date.month
    day = date.day

    if (month == 12 and day >= 21) or (1 <= month <= 2) or (month == 3 and day < 20):
        return "Winter"
    elif (month == 3 and day >= 20) or (4 <= month <= 5) or (month == 6 and day < 21):
        return "Spring"
    elif (month == 6 and day >= 21) or (7 <= month <= 8) or (month == 9 and day < 22):
        return "Summer"
    else:
        return "Autumn"

if __name__ == '__main__':
    app.run(debug=True)
