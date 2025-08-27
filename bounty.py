import json
from account import Account

path = "bounty_rankings/user_top"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/bounty.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
