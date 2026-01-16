import pandas as pd
from kickbase_api.league import get_league_activities, get_league_ranking

def calc_manager_budgets(token, league_id, league_start_date, start_budget):
    activities = get_league_activities(token, league_id, league_start_date)
    managers = get_league_ranking(token, league_id)
    
    manager_list = []
    for m in managers:
        # Hier greifen wir jetzt sicher auf die Namen (n) und IDs (i) zu
        m_name = m.get("n")
        m_id = m.get("i")
        current_cash = float(start_budget)
        
        for msg in activities:
            if msg.get("dt", "") < league_start_date:
                continue
            
            # Typ 15 = Transfer
            if msg.get("t") == 15:
                d = msg.get("data", {})
                price = float(d.get("trp", 0))
                # Prüfung ob Manager Käufer oder Verkäufer ist
                if str(d.get("byr")) == m_id:
                    current_cash -= price
                if str(d.get("slr")) == m_id:
                    current_cash += price
            
            # Typ 26 = Achievements
            elif msg.get("t") == 26:
                if str(msg.get("u")) == m_id:
                    current_cash += float(msg.get("data", {}).get("er", 0))
                    
        manager_list.append({
            "User": m_name,
            "Budget": current_cash,
            "Team Value": 0,
            "Available Budget": current_cash
        })
        
    return pd.DataFrame(manager_list)
