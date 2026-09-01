import sqlite3
import os
from datetime import datetime
from database import get_connection_to_db



def load_data_from_db():
    """ Fetches weather data from DB and converts into Python dictionary list
    Uses sqlite3.Row for key-value column mapping"""
    conn = get_connection_to_db() # Connects DB
    conn.row_factory = sqlite3.Row #Access columns by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    data_list = []
    for row in rows:
        data_list.append(dict(row))  # makes a dictionary for every recording and adds it into data list

    conn.close()
    return data_list


def build_markov_matrix(data_list):
    """ Builds markov matrix of weather data. Takes data after rearranging it into dictionaries (load_data_from_db)
    Returns a dictionary with transition analysis
    Example: {'CLEAR': {'CLEAR': 134, 'FEW_CLOUDS': 48, 'CLOUDY': 10, 'BROKEN_CLOUDS': 8, 'RAINY': 3}"""

    valid_entries = []
    for entry in data_list:
        if entry.get("pressure") is not None:   # validate records with pressure only
            valid_entries.append(entry)

    transitions = {}

    for i in range(len(valid_entries) - 1):  # gets through every record
        entry1 = valid_entries[i]
        entry2 = valid_entries[i + 1]

        t1 = datetime.strptime(entry1["timestamp"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(entry2["timestamp"], "%Y-%m-%d %H:%M:%S")

        hours_passed = (t2 - t1).total_seconds() / 3600

        if hours_passed > 4 or hours_passed <0:  # Makes sure there is no time gap between recordings
            continue

        current = entry1["state"]
        next_state = entry2["state"]

        if current not in transitions:
            transitions[current] = {}   # Creates new dictionary of transition of a certain state

        if next_state not in transitions[current]: # Checks if the next state already exist in dictionary of a certain state
            transitions[current][next_state] = 1 # if not, creates the first case of transition in states
        else:
            transitions[current][next_state] = transitions[current][next_state] + 1  # if first case already exists, just add a new one to transition history
    return transitions


def get_statistics_coefficient(data_list):
    """ Takes numbers of transition analysis from Markov matrix
    and arrange it into coefficients.
    Example: {'CLEAR': {'CLEAR': 0.66, 'FEW_CLOUDS': 0.24, 'CLOUDY': 0.05, 'BROKEN_CLOUDS': 0.04, 'RAINY': 0.01}"""
    transitions = build_markov_matrix(data_list)
    final_coefficient = {}

    for state in transitions: # Takes every state from Markov matrix for example: CLEAR
        total_exits = 0  # Counts how many transitions from the state were in total
        for target in transitions[state]:
            total_exits += transitions[state][target] # adds number of all cases of transition from one state to another
        if total_exits == 0:
            continue
        final_coefficient[state] = {}
        for target in transitions[state]: # takes every time only one transition (from CLEAR to CLOUDY for ex.)
            count = transitions[state][target] # gets numbers from markov matrix how many time this transition occurred
            final_coefficient[state][target] = round((count / total_exits), 2) # calculates the coefficient for every transition for every state
    return final_coefficient

def test(db_file):
    conn = sqlite3.connect(get_bd_path(db_file))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather LIMIT 15")
    rows = cursor.fetchall()

    raw_row = rows[0]
    print(f"1. How the object looks: {raw_row}")
    print(f"2. Access by the name: {raw_row['temp']}")
    print(f"3. After transformation into dictionary: {dict(raw_row)}")

def get_meteo_packet(data_list, target_hours):
    """ Being used to calculate delts of weather parameters over a specific time period,
      collect additional info to  use it for analytics.
      Args:
          data_list (list): a list of dictionaries retrieved from DB
          target_hours (int): time horizon for delta calculation
      Returns: Metrics, deltas, phase, pressure trend speed"""

    valid_data = [d for d in data_list if d.get("pressure") is not None]

    if len(valid_data) < 4:
        return None

    current = valid_data[-1] # Takes the last recording in the list



    steps = target_hours // 3  # determines one step as every 3 target hours as logger makes recordings every 3 hours
    past_index = max(0, len(valid_data) - steps - 1)  # takes index of the recording in list according to target hours (at which distance is analysis being proceed)
    past = valid_data[past_index]

    hour = int(current["timestamp"].split()[1][:2]) # Parses exact hour of recording
    phase = "DAY" if 6 <= hour < 21 else "NiGHT"  # Divides recordings into 2 day phases

    return {
        "current_state": current["state"],
        "p_delta" : current["pressure"] - past["pressure"],
        "h_delta" : current["humidity"] - past["humidity"],
        "t_delta" : current["temp"] - past["temp"],
        "hour": hour,
        "phase": phase,
        "trend_speed": (current["pressure"] - past["pressure"]) / target_hours
    }

def get_matrix_by_phase(data_list, is_day=True):
    """ Filters data by datetime or nighttime"""
    valid_entries = []

    for entry in data_list:
        if entry.get("pressure") is not None:
            valid_entries.append(entry)

    transitions = {}

    for i in range(len(valid_entries) - 1):
        entry1 = valid_entries[i]
        entry2 = valid_entries[i + 1]

        t1 = datetime.strptime(entry1["timestamp"], "%Y-%m-%d %H:%M:%S")
        t2 = datetime.strptime(entry2["timestamp"], "%Y-%m-%d %H:%M:%S")

        hours_passed = (t2 - t1).total_seconds() / 3600
        if hours_passed > 4 or hours_passed <0:
            continue

        entry_is_day = 6 <= t1.hour < 21
        if entry_is_day != is_day:
            continue

        current = entry1["state"]
        next_state = entry2["state"]

        if current not in transitions:
            transitions[current] = {}

        if next_state not in transitions[current]:
            transitions[current][next_state] = 1
        else:
            transitions[current][next_state] += 1

    final_coefficient = {}
    for state in transitions:
        total_exits = 0
        for target in transitions[state]:
            total_exits += transitions[state][target]
        if total_exits == 0:
            continue
        final_coefficient[state] = {}
        for target in transitions[state]:
            count = transitions[state][target]
            final_coefficient[state][target] = round((count / total_exits), 2)


    return final_coefficient
