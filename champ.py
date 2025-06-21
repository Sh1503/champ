import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="Football Predictor Pro",
    page_icon="⚽",
    layout="centered"
)
st.title("⚽ Football Match Predictor Pro")

# Teams per league (example teams or leave blank for automatic)
LEAGUE_TEAMS = {
    'Bundesliga': [...],
    'Premier League': [...],
    'La Liga': [...],
    'Ligue 1': [...],
    'Serie A': [...],
    'Israeli Premier League': [
        'Maccabi Haifa', 'Maccabi Tel Aviv', 'Hapoel Beer Sheva',
        'Beitar Jerusalem', 'Hapoel Tel Aviv', 'Hapoel Haifa',
        'Bnei Sakhnin', 'Hapoel Jerusalem', 'Maccabi Netanya',
        'Ironi Kiryat Shmona', 'Hapoel Hadera', 'Maccabi Petah Tikva',
        'Hapoel Petah Tikva', 'Sektzia Nes Tziona'
    ],
    'UEFA Champions League': [],
    'UEFA Europa League': [],
    'UEFA Conference League': []
}

# Load data from GitHub
def load_github_data(github_raw_url):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_league_data():
    data_sources = {
        "Premier League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/epl.csv",
        "La Liga": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/laliga.csv",
        "Serie A": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/seriea.csv",
        "Bundesliga": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/bundesliga.csv",
        "Ligue 1": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/ligue1.csv",
        "UEFA Champions League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/data/champions.csv",
        "UEFA Europa League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/data/europa.csv",
        "UEFA Conference League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/data/conference.csv",
        "Israeli Premier League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/data/israel_league_list.csv"
    }

    league_data = {}
    for league, url in data_sources.items():
        df = load_github_data(url)
        if df is not None:
            league_data[league] = df
    return league_data

# Match prediction logic
def predict_match(home_team, away_team, df):
    home_goals = df[df['HomeTeam'] == home_team]['FTHG'].mean()
    away_goals = df[df['AwayTeam'] == away_team]['FTAG'].mean()
    max_goals = 5
    home_win = draw = away_win = 0.0

    for i in range(max_goals+1):
        for j in range(max_goals+1):
            p = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p

    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals + away_goals, 1),
        "total_corners": get_corners_prediction(home_team, away_team, df)
    }

def get_corners_prediction(home_team, away_team, df):
    if 'HC' in df.columns and 'AC' in df.columns:
        home_corners = df[df['HomeTeam'] == home_team]['HC'].mean()
        away_corners = df[df['AwayTeam'] == away_team]['AC'].mean()
        return round(home_corners + away_corners, 1)
    return None

# Interface
data = load_league_data()
selected_league = st.selectbox("בחר ליגה", options=list(data.keys()))

if selected_league in data and not data[selected_league].empty:
    teams = LEAGUE_TEAMS[selected_league] if LEAGUE_TEAMS[selected_league] else (
        sorted(set(data[selected_league]['HomeTeam'].unique()) | set(data[selected_league]['AwayTeam'].unique()))
    )
    col1, col2 = st.columns(2)

    with col1:
        home_team = st.selectbox("קבוצה ביתית", options=teams)

    with col2:
        away_team = st.selectbox("קבוצה אורחת", options=[t for t in teams if t != home_team])

    if st.button("חשב חיזוי ⚡"):
        prediction = predict_match(home_team, away_team, data[selected_league])
        st.subheader("🔮 תוצאות חיזוי:")
        st.metric(label=f"ניצחון ל־{home_team}", value=f"{prediction['home_win']*100:.1f}%")
        st.metric(label="תיקו", value=f"{prediction['draw']*100:.1f}%")
        st.metric(label=f"ניצחון ל־{away_team}", value=f"{prediction['away_win']*100:.1f}%")

        st.divider()
        st.subheader("📊 סטטיסטיקות נוספות")
        st.write(f"שערים צפויים: **{prediction['total_goals']}**")
        if prediction['total_corners'] is not None:
            st.write(f"קרנות צפויות: **{prediction['total_corners']}**")
        else:
            st.warning("אין נתוני קרנות זמינים עבור ליגה זו")
else:
    st.error("לא נמצאו נתונים עבור הליגה הנבחרת")
