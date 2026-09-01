from datetime import datetime
from predict import predict_ladder
from stats import load_data_from_db


def validate_model(target_hours=3, test_samples=300):
    """
    Evaluates the accuracy and confidence of the probabilistic Monte-Carlo weather model
    against historical database records.
    """
    data = load_data_from_db()
    total_records = len(data)

    target_step = target_hours // 3
    min_required_history = 15

    if total_records < min_required_history + target_step:
        print("There is not enough historical data to evaluate (must be more than 15 records)")
        return

    # Calculate sampling stride to evenly step across historical records
    step = (total_records - 15 - target_step) // test_samples
    if step < 1:
        step = 1

    total_confidence = 0      # Actual state probability percentage
    correct_top_guesses = 0  # Counter for most-likely state matches
    total_tests = 0

    print(f"Starting validation of the model on {test_samples} historical samples...")
    print("-" * 65)

    start_index = max(50,15 + target_step)  #starting from 50th index in order to operate with enough quantity of records for Markov matrix

    for i in range(start_index, total_records - target_step, step):  # stops at index
        current_entry = data[i]  # at every entry takes one record under i index

        if current_entry.get("pressure") is None:
            continue

        t1 = datetime.strptime(
            current_entry["timestamp"], "%Y-%m-%d %H:%M:%S"
        )

        real_future_entry = None
        for j in range(i + 1, min(i + 30, total_records)): # doesn`t allow to
            candidate = data[j]
            if candidate.get("pressure") is None:
                continue

            t2 = datetime.strptime(
                candidate["timestamp"], "%Y-%m-%d %H:%M:%S"
            )
            hours_passed = (t2 - t1).total_seconds() / 3600

            if abs(hours_passed - target_hours) <= 1.5:  # makes sure function operates with a correct record
                real_future_entry = candidate
                break

        if not real_future_entry:
            continue

        # Provide historical records up to current evaluation point
        history_so_far = data[0: i + 1]

        # Run Monte Carlo simulation for target horizon (1000 runs for efficiency)
        predictions = predict_ladder(target_hours, history_so_far, num_sims=1000)

        if not predictions or len(predictions) < target_step:
            continue

        # Extract probability dict for the target forecast step
        # Target step index is target_step - 1 (e.g., step 1 index is 0)
        step_data = predictions[target_step - 1]
        probs = step_data["probabilities"]

        # Evaluate predicted vs actual state
        actual_state = real_future_entry["state"]

        # Confidence assigned by model to the actual outcome
        actual_prob = probs.get(actual_state, 0)
        total_confidence += actual_prob

        # Model's primary forecast choice
        top_state = max(probs, key=probs.get) if probs else "NONE"
        if top_state == actual_state:
            correct_top_guesses += 1

        total_tests += 1

        print(
            f"Test #{total_tests:02d} | Actual state: {actual_state:<12} | Model predicted: {actual_prob:>3}% | (Top prediction: {top_state})"
        )

    if total_tests > 0:
        avg_confidence = total_confidence / total_tests
        top_accuracy = (correct_top_guesses / total_tests) * 100

        print("=" * 65)
        print(f"RESULTS OF MODEL VALIDATION({total_tests} test were conducted):")
        print(
            f"1. Average confidence for the outcome: {avg_confidence:.1f}%"
        )
        print(
            f"2. Strict accuracy by top prediction: {top_accuracy:.1f}%"
        )
        print("=" * 65)


if __name__ == "__main__":
    validate_model(target_hours=6, test_samples=300)