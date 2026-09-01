import time
from predict import predict_ladder, display_forecast, get_meteo_packet
from stats import load_data_from_db

# Loading data from DB
data_history = load_data_from_db()

# A start time when script started
start_time = time.time()

# Preparing data for the predict function and execute Monte Carlo simulations
meteo_packet = get_meteo_packet(data_history, 9)
prediction_report = predict_ladder(12, data_history, num_sims=10000)

# A time when script has been completed
execution_time = time.time() - start_time

# Using display function to check results
display_forecast(meteo_packet, prediction_report, execution_time)