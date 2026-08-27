from modules.history import get_all_champions, get_season_results, get_constructor_champions

champions = get_all_champions()
print(f"Total champions: {len(champions)}")
print(champions[-1])  # most recent champion

results = get_season_results(2023)
print(f"\n2023 race winners: {len(results)}")
print(results[0])

constructors = get_constructor_champions()
print(f"\nTotal constructor champions: {len(constructors)}")
print(constructors[-1])
