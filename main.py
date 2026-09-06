import time
from datetime import datetime
from predict import predict_ladder, display_forecast, get_meteo_packet
from stats import load_data_from_db
from logger_database import log_weather_db

# Maximum allowed age for historical data before update
MAX_AGE_SECONDS = 4 * 3600

def ensure_data_freshness():
    """Validates the freshness of the latest database record.
    Triggers an API if the data is outdated or falls back to
    Historical Demo Mode if the network/API request fails."""

    data_history = load_data_from_db()

    #Handle empty database case
    if not data_history:
        print("! Data base is empty")
        return []

    # Parse timestamp from string to datetime object and calculate data age
    raw_last_data_record = data_history[-1]["timestamp"]
    last_record_time= datetime.strptime(raw_last_data_record, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    age_seconds = (current_time - last_record_time).total_seconds()

    # Evaluates whether an update is required
    if age_seconds > MAX_AGE_SECONDS:
        hours_outdated = round(age_seconds / 3600, 1)
        print(f"⚠️ Data in database is outdated (last record {hours_outdated} hours ago)")
        print(f"⚙️ Automatic fetching fresh data via API..")

        try:
            # Attempt to fetch and store a new record via API
            logged_weather = log_weather_db()
            if logged_weather:
                print("✅ New data has been logged")
                return load_data_from_db()
        except Exception as e:
            # Avoid application crash if API call fails
            print(f"❌ Error: {e}")
            print(f"Entering 'Historical Demo Mode'. Prediction is being build on the last recorded data in database")
    else:
        print("✅ Database has an actual data")

    return data_history


if __name__ == "__main__":
    # A start time when script started
    start_time = time.time()

    data_history = ensure_data_freshness()

    # Preparing data for the predict function and execute Monte Carlo simulations
    meteo_packet = get_meteo_packet(data_history, 9)
    prediction_report = predict_ladder(12, data_history, num_sims=10000)

    # A time when script has been completed
    execution_time = time.time() - start_time

    # Using display function to check results
    display_forecast(meteo_packet, prediction_report, execution_time)


