import json
from account import Account

path = "run_game_events/ranking_top?run_game_event_id=2&run_game_event_stage_num=0"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/run.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
