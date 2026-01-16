import pandas as pd
from kickbase_api.league import get_league_activities, get_league_ranking

def calc_manager_budgets(token, league_id, league_start_date, start_budget):
    # Holt alle Transfers und Prämien aus dem News-Feed
    trading, _, achievements = get_league_activities(token, league_id, league_start_date)
    # Holt die Liste aller Manager der Liga
    managers = get_league_ranking(token, league_id)
    
    manager_list = []
    for m in managers:
        m_name = m["n"]
        m_id = m["i"]
        
        # JEDER startet mit deinen 200.000.000
        current_cash = float(start_budget)
        
        # JEDEN Trade im Feed prüfen
        for t in trading:
            price = float(t.get("trp", 0))
            # Wenn Manager-ID der Käufer ist -> Geld abziehen
            if str(t.get("byr")) == str(m_id):
                current_cash -= price
            # Wenn Manager-ID der Verkäufer ist -> Geld addieren
            if str(t.get("slr")) == str(m_id):
                current_cash += price
        
        # Prämien (Achievements) dazurechnen
        for a in achievements:
            if str(a.get("u")) == str(m_id):
                current_cash += float(a.get("er", 0))
                
        manager_list.append({
            "User": m_name,
            "Budget": current_cash,
            "Team Value": 0,
            "Available Budget": current_cash
        })
        
    return pd.DataFrame(manager_list)
