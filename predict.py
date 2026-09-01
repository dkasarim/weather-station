from stats import load_data_from_db, get_meteo_packet,get_matrix_by_phase, get_statistics_coefficient
import random
from collections import Counter
import analyzer
from weather_api import get_weather

# city = "Holzminden"

def make_prediction():
    data = load_data_from_db()
    if not data:
        return "Not enough data"
    coefficients = get_statistics_coefficient(data)

    current_w = get_weather()
    if not current_w:
        return "Failed to retrieve current weather data"

    current_state = current_w["state"]
    coefficients_for_current_state = coefficients[current_state]
    if current_state not in coefficients:
        return f"Not enough data of {current_state}"
    best_state = ""
    max_prob = 0

    for state_name, coefficient in coefficients_for_current_state.items():
        if coefficient > max_prob:
            max_prob = coefficient
            best_state = state_name
    return f"Most likely will be {best_state} (chance {max_prob * 100}%)"


def predict_ladder(target_hours, data_history, num_sims=10000):
    '''Builds Monte-Carlo simulations to predict multi-step future weather states,
    taking pressure delta, basic Markov Matrix into account'''

    # Builds basic Markov matrix split by phase (day/night)
    matrix_day = get_matrix_by_phase(data_history, is_day=True)
    matrix_night = get_matrix_by_phase(data_history, is_day=False)

    # Retrieves latest weather data from DB
    meteo_packet = get_meteo_packet(data_history, 9)

    if not meteo_packet:
        return []

    initial_state = meteo_packet["current_state"]
    current_hour = meteo_packet["hour"]
    p_force = meteo_packet["p_delta"]
    decay_factor = 0.88  # exponential decay factor (per step) of pressure influence on the basic matrix

    steps = target_hours // 3

    step_biases = {}
    state_types = set(matrix_day.keys()) | set(matrix_night.keys())  # Sets all probable states of weather into one list


    # Pre-calculates dynamic biases for all further simulation steps to prevent heavy calls
    for i in range(1, steps + 1):  # adding one to steps, since function doesn`t count with the last number
        future_hour = (current_hour + i * 3) % 24  # using %24 to stay withing 24 time system
        step_is_day = 6 <= future_hour < 21    # Determine diurnal phase for the future step
        current_influence = p_force * (decay_factor ** i)  #calculates influence of pressure withing every step, taking decay factor into account
        rounded_p_delta = round(current_influence) # need to round delta for DB matching

        # Fetch historical trend biases for all states at step i
        step_biases[i] = {}
        for state in state_types:
            step_biases[i][state] = analyzer.get_dynamic_biases(rounded_p_delta, state, is_day=step_is_day, trend_hours = 9)


    all_simulation_results = {}
    for i in range(1 ,steps + 1):
        all_simulation_results[i] = []  # records all simulations for each next step


    # Execute Monte Carlo simulations
    for num in range(num_sims):
        state = initial_state
        for i in range(1, steps + 1):
            future_hour = (current_hour + i * 3) % 24
            is_day = 6 <= future_hour < 21
            if is_day:
                current_matrix = matrix_day
            else:
                current_matrix = matrix_night

            probs = current_matrix.get(state, {})  #takes only basic probabilities of the next states for a current state of weather
            if not probs:
                probs = {state: 1.0}

            dynamic_biases = step_biases[i].get(state, {}) # gets probabilities for a current state accordingly to pressure analys at step i

            adjusted_probs = {}
            total_new_weight = 0

            for next_state, p in probs.items():  # Takes every possible next state and probabilities for a current state
                bias = dynamic_biases.get(next_state, 1.0)

                new_p = bias * p # calculates new pressure coefficient
                adjusted_probs[next_state] = new_p # build new matrix with updated probabilities
                total_new_weight += new_p

            # Downgrades to base probabilities if all weights are zeros
            if total_new_weight == 0:
                adjusted_probs = probs
                total_new_weight = sum(probs.values())

            final_states =[]
            final_weights = []

            for s,w in adjusted_probs.items():
                final_states.append(s)
                final_weights.append(w / total_new_weight)  # Normalizing weights, so probs sum up to 1.0


            # states_list = list(adjusted_probs.keys())
            # weights_list = list(adjusted_probs.values())

            # Execute weighted random choice
            state = random.choices(final_states, weights=final_weights, k = 1)[0]
            all_simulation_results[i].append(state)


    # Forms statistics for final report
    prediction_report = []

    # Iterate throgh all simualtion steps
    for i in range(1, steps + 1):
        furthest_hour = (current_hour + i * 3) % 24
        counts = Counter(all_simulation_results[i]) #Count occurrences of each weather state across all simulations for step i

        probabilities = {} # Converts counts into a dictionary state:percentage
        list_of_strings = []
        #Iterate over weather states from most to least common
        for state_name, count in counts.most_common():
            percentage = int((count / num_sims) * 100) #Convers count of states into percentage relative to all simulations
            probabilities[state_name] = percentage


        time_label = f"{furthest_hour:02d}:00"
        prediction_report.append({
            "time": time_label,
            "hour": furthest_hour,
            "probabilities": probabilities,
    })

    return prediction_report


def display_forecast(meteo_packet, prediction_report, execution_time):
    """
    Formats and prints the simulation output to the console
    """
    if not meteo_packet or not prediction_report:
        print("Not enough data")
        return

    # Extract starting metadata
    start_time = f"{meteo_packet['hour']:02d}:00"
    start_state = meteo_packet["current_state"]
    p_delta = meteo_packet["p_delta"]

    # Print Header
    print(f"Beginning states: Time: {start_time}, State: {start_state}, Pressure delta: {p_delta}")
    print("-" * 50)
    print("\nScript is activated")

    # Format and print step-by-step probabilities
    for step in prediction_report:
        time_label = step["time"]

        # Build probability strings (e.g. "FEW_CLOUDS: 32%")
        prob_strings = [
            f"{state}: {percentage}%"
            for state, percentage in step["probabilities"].items()
        ]
        stats_str = ", ".join(prob_strings)

        print(f"{time_label} -- {stats_str}")

    # Print execution time summary
    print(f"\nTime of execution of the script: {execution_time:.4f} seconds")
