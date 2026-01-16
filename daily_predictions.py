from features.predictions.predictions import live_data_predictions, join_current_market, join_current_squad
from features.predictions.preprocessing import preprocess_player_data, split_data
from features.predictions.modeling import train_model, evaluate_model
from kickbase_api.user import login
from features.notifier import send_mail
from features.predictions.data_handler import (
    create_player_data_table,
    check_if_data_reload_needed,
    save_player_data_to_db,
    load_player_data_from_db,
)
from features.budgets import calc_manager_budgets
from dotenv import load_dotenv
import os
import pandas as pd

# -------------------------------------------------
# LOAD ENV
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# SYSTEM SETTINGS (NICHT ÄNDERN)
# -------------------------------------------------
last_mv_values = 365
last_pfm_values = 50

features = [
    "p",
    "mv",
    "days_to_next",
    "mv_change_1d",
    "mv_trend_1d",
    "mv_change_3d",
    "mv_vol_3d",
    "mv_trend_7d",
    "market_divergence",
]

target = "mv_target_clipped"

pd.options.display.float_format = lambda x: "{:,.0f}".format(x).replace(",", ".")
pd.set_option("display.max_columns", None)

# -------------------------------------------------
# USER SETTINGS
# -------------------------------------------------
competition_ids = [1]                 # Bundesliga
league_start_date = "2025-12-27"      # Startdatum der Liga
start_budget = 200_000_000            # Startbudget eurer Liga
EMAIL_TO = os.getenv("EMAIL_USER")

# -------------------------------------------------
# LOGIN
# -------------------------------------------------
KICK_USER = os.getenv("KICK_USER")
KICK_PASS = os.getenv("KICK_PASS")
KICK_LEAGUE_ID = os.getenv("KICK_LEAGUE_ID")

if not KICK_USER or not KICK_PASS:
    raise Exception("KICK_USER oder KICK_PASS fehlt in GitHub Secrets")

if not KICK_LEAGUE_ID:
    raise Exception("KICK_LEAGUE_ID fehlt in GitHub Secrets")

token = login(KICK_USER, KICK_PASS)
print("Logged in to Kickbase")

league_id = int(KICK_LEAGUE_ID)
print(f"Using league ID: {league_id}")

# -------------------------------------------------
# BUDGETS (GESCHÄTZT FÜR ANDERE)
# -------------------------------------------------
manager_budgets_df = calc_manager_budgets(
    token, league_id, league_start_date, start_budget
)

# -------------------------------------------------
# DATA
# -------------------------------------------------
create_player_data_table()
reload_data = check_if_data_reload_needed()
save_player_data_to_db(
    token,
    competition_ids,
    last_mv_values,
    last_pfm_values,
    reload_data,
)
player_df = load_player_data_from_db()

# -------------------------------------------------
# MODEL
# -------------------------------------------------
proc_player_df, today_df = preprocess_player_data(player_df)
X_train, X_test, y_train, y_test = split_data(proc_player_df, features, target)

model = train_model(X_train, y_train)
evaluate_model(model, X_test, y_test)

# -------------------------------------------------
# PREDICTIONS
# -------------------------------------------------
live_predictions_df = live_data_predictions(today_df, model, features)

market_recommendations_df = join_current_market(
    token, league_id, live_predictions_df
)

squad_recommendations_df = join_current_squad(
    token, league_id, live_predictions_df
)

# -------------------------------------------------
# MAIL
# -------------------------------------------------
send_mail(
    manager_budgets_df,
    market_recommendations_df,
    squad_recommendations_df,
    EMAIL_TO,
)

print("DONE")
