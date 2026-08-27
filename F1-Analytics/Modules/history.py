import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def get_all_champions() -> list[dict]:
    champions = []
    for season in range(1950, 2025):
        url = f"{BASE_URL}/{season}/driverStandings/1.json"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        data = response.json()
        standings = data["MRData"]["StandingsTable"]["StandingsLists"]
        if not standings:
            continue
        entry = standings[0]
        driver = entry["DriverStandings"][0]["Driver"]
        constructor = entry["DriverStandings"][0]["Constructors"][0]
        champions.append({
            "season": season,
            "driver": f"{driver['givenName']} {driver['familyName']}",
            "nationality": driver["nationality"],
            "constructor": constructor["name"],
            "points": entry["DriverStandings"][0]["points"]
        })
    return champions

def get_season_results(season: int) -> list[dict]:
    url = f"{BASE_URL}/{season}/results/1.json?limit=100"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    results = []
    for race in races:
        winner = race["Results"][0]
        results.append({
            "round": race["round"],
            "race": race["raceName"],
            "circuit": race["Circuit"]["circuitName"],
            "winner": f"{winner['Driver']['givenName']} {winner['Driver']['familyName']}",
            "constructor": winner["Constructor"]["name"],
            "laps": winner["laps"],
            "time": winner.get("Time", {}).get("time", "N/A")
        })
    return results

def get_constructor_champions() -> list[dict]:
    champions = []
    for season in range(1958, 2025):
        url = f"{BASE_URL}/{season}/constructorStandings/1.json"
        response = requests.get(url)
        if response.status_code != 200:
            continue
        data = response.json()
        standings = data["MRData"]["StandingsTable"]["StandingsLists"]
        if not standings:
            continue
        entry = standings[0]
        constructor = entry["ConstructorStandings"][0]["Constructor"]
        champions.append({
            "season": season,
            "constructor": constructor["name"],
            "nationality": constructor["nationality"],
            "points": entry["ConstructorStandings"][0]["points"]
        })
    return champions
