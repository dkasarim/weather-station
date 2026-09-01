# 🌤️ Weather Forecasting Engine (Markov Chain & Monte Carlo)

[English](#english) | [German/Deutsch](#deutsch)

---

## English

> 🎓 **Educational Project Disclaimer:**  
> This is a hands-on learning project built to practice Python, SQLite database management, **Markov Chains**, and **Monte Carlo simulations**. It is designed as an educational experiment in probabilistic modeling rather than a production-ready commercial forecasting tool.

### 📌 Project Overview
This is a self-hosted Python system designed for collecting meteorological data and generating weather forecasts. Instead of relying on pre-built third-party forecast models, this engine logs real-time weather metrics into a local SQLite database via the OpenWeatherMap API. It then computes short-term weather state probabilities using **diurnal Markov Chains** combined with **Monte Carlo simulations**.

The predictive engine continuously calculates pressure trends ($\Delta P$) over time windows and applies dynamic bias adjustments, exponential decay factors, and Laplace smoothing to historical transition matrices.

> ⚠️ **Important Note on Data Dependency:**  
> The Markov Chain model relies on historical weather transition records. Without history, the system cannot build transition matrices.  
> * **Included Demo Data:** A pre-collected database for **Holzminden** (`weather.db`) is included in this repository so you can test forecasts immediately out of the box.
> * **Custom Cities:** To run predictions for another location, you must leave `logger_database.py` running in the background to accumulate local history over time.

### 🏗️ File Architecture
* `config.py` — Centralized application settings and absolute path resolution using `python-dotenv`.
* `weather_api.py` — OpenWeatherMap API wrapper that maps weather codes to standardized `WeatherState` Enums.
* `database.py` — SQLite schema definition and initial database connection setup.
* `logger_database.py` — Background service that fetches and logs weather parameters every 3 hours.
* `stats.py` — Statistical utility functions for data extraction and building Day/Night Markov matrices.
* `analyzer.py` — Core trend analysis module calculating dynamic bias factors based on historical pressure changes.
* `predict.py` — Monte Carlo simulation engine that builds probability ladders for multi-step predictions.
* `validator.py` — Model evaluation tool for backtesting predictive accuracy against historical database records.
* `main.py` — Main entry point to run the forecast simulation.

### ⚙️ How to Adjust the Forecast Horizon
You can easily customize the prediction timeframe inside `main.py`:
```python```
Pass the desired number of hours (e.g., 6, 12, 24) as the first argument to predict_ladder
prediction_report = predict_ladder(12, data_history, num_sims=10000)


### 🚀 Quick Start Guide

1. Clone the repository: 
git clone [https://github.com/YOUR_USERNAME/weather-station.git](https://github.com/YOUR_USERNAME/weather-station.git)
cd weather-station

2.Install dependencies: 
pip install -r requirements.txt

3. Configure the .env file:
* Get a free API Key at OpenWeatherMap API. (https://openweathermap.org/)
* Create a new file named .env in the root folder (or copy .env.example).
* Fill in your credentials:

WEATHER_API_KEY=your_openweather_api_key
WEATHER_CITY=your_city
WEATHER_DB_NAME=database_file_name

4. Run Forecast Simulation (Using pre-packaged weather.db):

python main.py

5. Start Data Logging (Required for continuous operation):

python logger_database.py


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


## German/Deutsch 


🎓 Hinweis zum Lernprojekt:

Dies ist ein praktisches Lehrprojekt zur Vertiefung von Python, SQLite, Markov-Ketten und Monte-Carlo-Simulationen. Es dient als bildungsorientiertes Experiment zur probabilistischen Modellierung und nicht als kommerzieller Wetterdienst.



###📌 ProjektübersichtDies ist ein eigenständig entwickeltes Python-System zur Erfassung von Wetterdaten und zur Berechnung lokaler Wettervorhersagen. Anstatt vorgefertigte Vorhersagedienste zu nutzen, speichert das Skript Echtzeit-Meteorologiedaten über die OpenWeatherMap-API in einer lokalen SQLite-Datenbank. Die Berechnung zukünftiger Wetterzustände erfolgt über tageszeitabhängige Markov-Ketten in Kombination mit Monte-Carlo-Simulationen. 

Das System analysiert Luftdrucktrends ($\Delta P$) und wendet dynamische Korrekturfaktoren, exponentielle Dämpfung sowie Laplace-Glättung auf historische Übergangsmatrizen an.

>⚠️ Wichtiger Hinweis zur Datenbasis:
> Das Markov-Modell benötigt historische Zustandswechsel. Ohne Datenbasis können keine Matrizen berechnet werden.
> * ** Enthaltene Demodaten: Eine Datenbank mit Daten für Holzminden (weather.db) ist im Repository enthalten, damit Prognosen direkt getestet werden können.
> * ** Andere Städte: Für neue Orte muss logger_database.py im Hintergrund laufen, um schrittweise eine Historie aufzubauen.

###🏗️ Dateistruktur
*config.py — Zentrale Konfiguration und Pfadverwaltung mittels python-dotenv.
*weather_api.py — API-Client, der rohe Wetter-IDs in standardisierte WeatherState-Enums umwandelt.
*database.py — Initialisierung der SQLite-Datenbankstruktur.
*logger_database.py — Hintergrunddienst, der alle 3 Stunden neue Daten erfasst.
*stats.py — Berechnung der Markov-Übergangsmatrix (getrennt nach Tag- und Nachtphasen).
*analyzer.py — Analyse-Modul zur Berechnung dynamischer Wahrscheinlichkeitsanpassungen basierend auf Luftdruckänderungen.
*predict.py — Monte-Carlo-Simulationsengine für mehrstufige Zustandsprognosen.
*validator.py — Backtesting-Modul zur Überprüfung der Modellgenauigkeit anhand historischer Daten.
*main.py — Hauptskript zur Ausführung der Wettervorhersage.

### ⚙️ Vorhersagehorizont anpassen
Der gewünschte Zeitraum für die Prognose kann direkt in der main.py angepasst werden:

# Übergebe die gewünschte Anzahl an Stunden (z. B. 6, 12, 24) als erstes Argument an predict_ladder
prediction_report = predict_ladder(12, data_history, num_sims=10000)


###🚀 Schritt-für-Schritt Anleitung

1. Repository klonen:
git clone [https://github.com/DEIN_USERNAME/weather-station.git](https://github.com/DEIN_USERNAME/weather-station.git)
cd weather-station

2. Abhängigkeiten installieren:
pip install -r requirements.txt

3. .env-Datei einrichten:
* Registriere dich für einen kostenlosen API-Schlüssel auf OpenWeatherMap API.  (https://openweathermap.org/)
* Erstelle eine Datei namens .env im Hauptverzeichnis (siehe .env.example).
* Trage deine Daten ein:

WEATHER_API_KEY=dein_openweather_api_key
WEATHER_CITY=deine_Stadt
WEATHER_DB_NAME=weather.db

4. Vorhersage ausführen (mit mitgelieferter weather.db):

python main.py

5. Laufende Datenerfassung starten:

python logger_database.py
