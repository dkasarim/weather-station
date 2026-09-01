from stats import load_data_from_db, get_matrix_by_phase
from datetime import datetime


def get_dynamic_biases(current_p_delta, current_state, is_day=True, trend_hours=9):
    """Calculates dynamic probability adjustment factors (biases) based on historical weather patterns.

    Executes in-memory Python validation over raw DB records to ensure high speed.
    """
    data = load_data_from_db()

    # Fetch baseline probabilities for current phase(day or night)
    base_matrix = get_matrix_by_phase(data, is_day=is_day)
    base_probs = base_matrix.get(current_state, {})

    if not base_probs:
        return {}

    # Filter entries that have pressure data

    valid_entries = []
    for entry in data:
        if entry["pressure"] is not None:
            valid_entries.append(entry)

    # Calculate offset steps: 9 hours trend = 3 steps back (since 1 step = 3h)
    steps_back =  trend_hours // 3
    matched_next_states = []

    # Iterate through entries maintaining a 9-hour past window and a 3-hour future prediction target
    for i in range(steps_back, len(valid_entries) - 1):
        w0 = valid_entries[i - steps_back]  # Past (9 hours ago default)
        w1 = valid_entries[i]  # Present
        w2 = valid_entries[i + 1]  # Target future (+3 hours)

        t0 = datetime.strptime(w0["timestamp"], "%Y-%m-%d %H:%M:%S")
        t1 = datetime.strptime(w1["timestamp"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(w2["timestamp"], "%Y-%m-%d %H:%M:%S")

        # Validate temporal integrity (gap 0 -> 1 ~ trend_hours, gap 1 -> 2 ~ 3 hours)
        past_gap = (t1 - t0).total_seconds() / 3600
        future_gap = (t2 - t1).total_seconds() / 3600

        # Allow +/- 1 hour margin of error for logging timestamps
        if (trend_hours - 1 <= past_gap <= trend_hours + 1) and (
                2 <= future_gap <= 4
        ):
            historical_p_delta = w1["pressure"] - w0["pressure"]

            # Match similar trend intensity (within a tolerance band) and current state
            if (
                    historical_p_delta == current_p_delta
                    and w1["state"] == current_state
            ):
                matched_next_states.append(w2["state"])

    total_found = len(matched_next_states)
    biases = {}

    # If no historical trends match, return safe neutral multipliers
    if total_found == 0:
        return {state: 1.0 for state in base_probs.keys()}

    # Calculate smoothed biases
    for state in base_probs.keys():
        count = matched_next_states.count(state)

        # Add  pseudo-observation to avoid zero probability lockout
        smoothed_real_prob = (count + 0.01) / (total_found + 0.01 * len(base_probs)) #Laplace Additive Smoothing
        base_prob = base_probs.get(state, 0.01)

        # Calculate final bias ratio bounded to a reasonable window [0.1, 5.0]
        raw_bias = smoothed_real_prob / base_prob
        biases[state] = round(max(0.1, min(raw_bias, 5.0)), 2)

    return biases


if __name__ == '__main__':
    # Тест: находимся в CLOUDY, давление упало на 1.
    # Функция покажет, как изменились шансы для ВСЕХ состояний.
    print(f"Correction Coefficients: {get_dynamic_biases( 0, 'CLOUDY', is_day=True, trend_hours=9)}")



