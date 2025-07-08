from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

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


    """
    The function `interpolate_weather_data_for_times_net` extracts temperature data from weather
    entries, interpolates it to hourly frequency, and returns the first 48 hourly temperature values
    along with their corresponding timestamps.
    
    It fills the hourly gaps with data:
       [30.06, 27.64, 26.73, 30.65, 35.61, 37.9, 30.92, 28] # (every 3 hours) 
       TO ->>>
       [30.06, 29.2, 28.4, 27.64, 27.2, 26.9, ...]  # (hourly, 48 total)
    """
def interpolate_weather_data_for_times_net(weather_data):
    # Extract timestamps and temps
    timestamps = [entry["dt_txt"] for entry in weather_data]
    temps = [entry["main"]["temp"] for entry in weather_data]

    # Create datetime-indexed series
    df = pd.DataFrame({"temp": temps}, index=pd.to_datetime(timestamps))

    # Resample to hourly frequency
    hourly_df = df.resample("1h").interpolate("linear")

    # Keep only the first 48 values (2 days)
    hourly_temps = hourly_df["temp"].iloc[:48].tolist()
    hourly_times = hourly_df.index.strftime("%Y-%m-%d %H:%M").tolist()[:48]

    return hourly_temps, hourly_times


def plot_temp_difference(forecast, outdoor):
    temp_diff = forecast - outdoor
    fig, ax = plt.subplots(figsize=(10, 4))
    temp_diff.plot(ax=ax, label="Indoor - Outdoor Temp", color="orange")
    ax.set_title("Forecasted Temperature Difference")
    ax.set_ylabel("°C")
    ax.set_xlabel("Time")
    ax.legend()

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")