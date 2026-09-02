import fastf1
import pandas as pd

fastf1.Cache.enable_cache("cache")

def get_race_strategy(season: int, round: int) -> dict:
    session = fastf1.get_session(season, round, "R")
    session.load(telemetry=False, weather=False, messages=False)

    laps = session.laps[["Driver", "LapNumber", "Compound", "PitInTime", "PitOutTime", "LapTime"]].copy()
    laps = laps.dropna(subset=["Compound"])

    drivers = laps["Driver"].unique().tolist()

    strategy = {}
    for driver in drivers:
        driver_laps = laps[laps["Driver"] == driver].copy()
        stints = []
        current_compound = None
        stint_start = None

        for _, lap in driver_laps.iterrows():
            if lap["Compound"] != current_compound:
                if current_compound is not None:
                    stints.append({
                        "compound": current_compound,
                        "start_lap": stint_start,
                        "end_lap": int(lap["LapNumber"]) - 1
                    })
                current_compound = lap["Compound"]
                stint_start = int(lap["LapNumber"])

        if current_compound is not None:
            stints.append({
                "compound": current_compound,
                "start_lap": stint_start,
                "end_lap": int(driver_laps["LapNumber"].max())
            })

        strategy[driver] = stints

    return {
        "season": season,
        "round": round,
        "event": session.event["EventName"],
        "strategy": strategy
    }

def get_pit_stops(season: int, round: int) -> list[dict]:
    url = f"https://api.jolpi.ca/ergast/f1/{season}/{round}/pitstops.json?limit=100"
    import requests
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    stops = data["MRData"]["RaceTable"]["Races"]
    if not stops:
        return []
    pit_stops = []
    for stop in stops[0]["PitStops"]:
        pit_stops.append({
            "driver": stop["driverId"],
            "lap": stop["lap"],
            "stop": stop["stop"],
            "duration": stop["duration"]
        })
    return pit_stops

def get_lap_times(season: int, round: int, driver_code: str) -> list[dict]:
    session = fastf1.get_session(season, round, "R")
    session.load(telemetry=False, weather=False, messages=False)

    driver_laps = session.laps.pick_drivers(driver_code)[["LapNumber", "LapTime", "Compound", "Sector1Time", "Sector2Time", "Sector3Time"]].copy()
    driver_laps = driver_laps.dropna(subset=["LapTime"])

    results = []
    for _, lap in driver_laps.iterrows():
        results.append({
            "lap": int(lap["LapNumber"]),
            "lap_time": str(lap["LapTime"]),
            "compound": lap["Compound"],
            "sector1": str(lap["Sector1Time"]),
            "sector2": str(lap["Sector2Time"]),
            "sector3": str(lap["Sector3Time"])
        })
    return results
