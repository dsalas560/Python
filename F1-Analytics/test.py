from modules.dashboard import get_driver_standings, get_constructor_standings, get_race_schedule, get_race_results, CURRENT_SEASON

print(f"=== {CURRENT_SEASON} Driver Standings ===")
drivers = get_driver_standings()
for d in drivers[:3]:
    print(d)

print(f"\n=== {CURRENT_SEASON} Constructor Standings ===")
constructors = get_constructor_standings()
for c in constructors[:3]:
    print(c)

print(f"\n=== {CURRENT_SEASON} Race Schedule ===")
schedule = get_race_schedule()
for r in schedule[:3]:
    print(r)

print(f"\n=== {CURRENT_SEASON} Round 1 Results ===")
results = get_race_results(CURRENT_SEASON, 1)
for r in results[:3]:
    print(r)
