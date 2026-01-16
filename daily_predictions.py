import os
import pandas as pd
from dotenv import load_dotenv
from kickbase_api.user import login
from kickbase_api.league import get_league_id
from features.budgets import calc_manager_budgets
from features.notifier import send_mail
from features.predictions.data_handler import create_player_data_table, check_if_data_reload_needed, save_player_data_to_db, load_player_data_from_db
from features.predictions.preprocessing import preprocess_player_data, split_data
from features.predictions.modeling import train_model
from features.predictions.predictions import live_data_predictions, join_current_market, join_current_squad

load_dotenv()

# --- USER SETTINGS ---
LEAGUE_START = "2025-12-27" # Datum Rückrunden-Start
START_CASH = 200000000 # Deine 200 Mio
COMP_IDS = [1]

# --- LOGIN & LIGA ---
token = login(os.getenv("KICK_USER"), os.getenv("KICK_PASS"))
league_id = get_league_id(token, os.getenv("KICK_LEAGUE_ID"))

# 1. Budget Berechnung
budget_df = calc_manager_budgets(token, league_id, LEAGUE_START, START_CASH)

# 2. Marktwert Vorhersage
create_player_data_table()
reload = check_if_data_reload_needed()
save_player_data_to_db(token, COMP_IDS, 365, 50, reload)
player_df = load_player_data_from_db()
proc_df, today_df = preprocess_player_data(player_df)
feat = ["p", "mv", "days_to_next", "mv_change_1d", "mv_trend_1d", "mv_change_3d", "mv_vol_3d", "mv_trend_7d", "market_divergence"]
model = train_model(*split_data(proc_df, feat, "mv_target_clipped")[:2])
preds = live_data_predictions(today_df, model, feat)

# 3. Zusammenführung
market_df = join_current_market(token, league_id, preds)
squad_df = join_current_squad(token, league_id, preds)

# 4. Mail
send_mail(budget_df, market_df, squad_df, os.getenv("EMAIL_USER"))
print("RESTART ERFOLGREICH: Budgets individuell berechnet!")
