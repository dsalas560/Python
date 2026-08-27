import requests

BASE_URL = "https://api.jolpi.ca/ergast/f1"

def get_all_circuits() -> list[dict]:
    url = f"{BASE_URL}/circuits.json?limit=100"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    circuits = data["MRData"]["CircuitTable"]["Circuits"]
    return circuits

def get_circuit_by_id(circuit_id: str) -> dict | None:
    url = f"{BASE_URL}/circuits/{circuit_id}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    circuits = data["MRData"]["CircuitTable"]["Circuits"]
    return circuits[0] if circuits else None

def get_circuit_races(circuit_id: str) -> list[dict]:
    url = f"{BASE_URL}/circuits/{circuit_id}/results/1.json?limit=100"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    return races
