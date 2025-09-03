import json
import sqlite3
import time

from account import Account



# Returns most recent New World League ID
def get_event():
    conn = sqlite3.connect("./sakura.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT MstMapGameLeague_.serverId_
        FROM MstMapGameEvent_
        INNER JOIN MstMapGameLeague_ ON MstMapGameLeague_.mapGameEventId_ = MstMapGameEvent_.serverId_
        WHERE MstMapGameLeague_.leagueNumber_ = 3
        ORDER BY MstMapGameEvent_.startAT_ DESC LIMIT 1
       
    """
    cursor.execute(query)
    result = cursor.fetchone()
    if not result:
        print("Error: League ID not found")
        exit()

    event = { "nw": result["serverId_"] }
    return event


event = get_event()
path = f"map_game_leagues/{event["nw"]}/ranks?page=1"

accounts = [Account("gb"), Account("jp")]
for account in accounts:
    data = account.get(path)
    with open(f"output/{account.version}/tm.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
