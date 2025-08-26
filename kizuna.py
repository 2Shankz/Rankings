import json
from account import Account

path = "kizuna_battle_events/80/user_top_ranks"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/kizuna/{account.version}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
