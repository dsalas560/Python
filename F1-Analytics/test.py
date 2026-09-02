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


from modules.strategy import get_race_strategy, get_pit_stops

print("=== 2026 Round 1 Strategy ===")
strategy = get_race_strategy(2026, 1)
print(f"Event: {strategy['event']}")
for driver, stints in list(strategy['strategy'].items())[:3]:
    print(f"{driver}: {stints}")

print("\n=== 2026 Round 1 Pit Stops ===")
stops = get_pit_stops(2026, 1)
for s in stops[:5]:
    print(s)

from modules.cache import cached_call
from modules.history import get_all_champions

print("=== Cache Test ===")
# First call - fetches fresh
champions = cached_call("all_champions", get_all_champions)
print(f"Total champions: {len(champions)}")

# Second call - should serve from disk instantly
champions = cached_call("all_champions", get_all_champions)
print(f"Total champions (cached): {len(champions)}")
