import json
from account import Account

path = "pirates_arena_stages/315/rankings"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/pvp.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)