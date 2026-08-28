import requests
from datetime import datetime

BASE_URL = "https://api.jolpi.ca/ergast/f1"
CURRENT_SEASON = datetime.now().year

def get_driver_standings(season: int = CURRENT_SEASON) -> list[dict]:
    url = f"{BASE_URL}/{season}/driverStandings.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return []
    results = []
    for entry in standings[0]["DriverStandings"]:
        driver = entry["Driver"]
        constructor = entry["Constructors"][0]
        results.append({
            "position": entry["position"],
            "driver": f"{driver['givenName']} {driver['familyName']}",
            "code": driver.get("code", "N/A"),
            "nationality": driver["nationality"],
            "constructor": constructor["name"],
            "points": entry["points"],
            "wins": entry["wins"]
        })
    return results

def get_constructor_standings(season: int = CURRENT_SEASON) -> list[dict]:
    url = f"{BASE_URL}/{season}/constructorStandings.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    standings = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings:
        return []
    results = []
    for entry in standings[0]["ConstructorStandings"]:
        constructor = entry["Constructor"]
        results.append({
            "position": entry["position"],
            "constructor": constructor["name"],
            "nationality": constructor["nationality"],
            "points": entry["points"],
            "wins": entry["wins"]
        })
    return results

def get_race_schedule(season: int = CURRENT_SEASON) -> list[dict]:
    url = f"{BASE_URL}/{season}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    results = []
    for race in races:
        results.append({
            "round": race["round"],
            "race": race["raceName"],
            "circuit": race["Circuit"]["circuitName"],
            "locality": race["Circuit"]["Location"]["locality"],
            "country": race["Circuit"]["Location"]["country"],
            "date": race["date"],
            "time": race.get("time", "N/A")
        })
    return results

def get_race_results(season: int, round: int) -> list[dict]:
    url = f"{BASE_URL}/{season}/{round}/results.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    if not races:
        return []
    results = []
    for entry in races[0]["Results"]:
        driver = entry["Driver"]
        results.append({
            "position": entry["position"],
            "driver": f"{driver['givenName']} {driver['familyName']}",
            "code": driver.get("code", "N/A"),
            "constructor": entry["Constructor"]["name"],
            "laps": entry["laps"],
            "status": entry["status"],
            "points": entry["points"],
            "time": entry.get("Time", {}).get("time", "N/A"),
            "fastest_lap": entry.get("FastestLap", {}).get("Time", {}).get("time", "N/A")
        })
    return results
