from modules.circuits import get_all_circuits, get_circuit_by_id

circuits = get_all_circuits()
print(f"Total circuits: {len(circuits)}")
print(circuits[0])

monza = get_circuit_by_id("monza")
print(monza)
