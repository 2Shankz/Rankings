import json
from account import Account

path = "assault_rumble_event/rank/user/top"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/assrum.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
 