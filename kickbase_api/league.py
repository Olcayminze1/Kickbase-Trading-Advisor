from kickbase_api.config import BASE_URL, get_json_with_token

def get_league_id(token, league_identifier):
    league_infos = get_leagues_infos(token)
    league_id_str = str(league_identifier).strip()
    for league in league_infos:
        if str(league["id"]) == league_id_str or league["name"] == league_id_str:
            return league["id"]
    return league_infos[0]["id"]

def get_leagues_infos(token):
    url = f"{BASE_URL}/leagues/selection"
    data = get_json_with_token(url, token)
    return [{"id": str(item.get("i")), "name": item.get("n")} for item in data.get("it", [])]

def get_league_activities(token, league_id, league_start_date):
    # Wir laden 2500 News-Einträge
    url = f"{BASE_URL}/leagues/{league_id}/activitiesFeed?max=2500"
    data = get_json_with_token(url, token)
    return data.get("af", [])

def get_league_players_on_market(token, league_id):
    url = f"{BASE_URL}/leagues/{league_id}/market"
    data = get_json_with_token(url, token)
    return [{"id": str(p.get("i")), "prob": p.get("prob"), "exp": p.get("exs")} for p in data.get("it", [])]

def get_league_ranking(token, league_id):
    url = f"{BASE_URL}/leagues/{league_id}/ranking"
    data = get_json_with_token(url, token)
    # WICHTIG: Hier geben wir ein klares Wörterbuch zurück
    return [{"n": u["n"], "i": str(u["i"])} for u in data.get("us", [])]
