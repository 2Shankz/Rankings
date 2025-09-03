import json
import sqlite3
import time

from account import Account



# Returns run_game_event_id and run_game_event_stage_num needed for API request
def get_event():
    conn = sqlite3.connect("./sakura.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = "SELECT serverId_, startAt_ FROM MstRunGameEvent_ ORDER BY startAt_ DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    event = {
        "id": result["serverId_"],
        "stage": int((time.time() - result["startAt_"]) / 604800) # calculated as number of weeks since event started
    }
    return event



event = get_event()
path = f"run_game_events/ranking_top?run_game_event_id={event["id"]}&run_game_event_stage_num={event["stage"]}"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/run.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
