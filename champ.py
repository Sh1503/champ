# התקנת החבילות הנדרשות
# !pip install streamlit pandas numpy scipy requests

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO
import os

# הגדרות דף
st.set_page_config(
    page_title="Football Predictor Pro",
    page_icon="⚽",
    layout="centered"
)
st.title("⚽ Football Match Predictor Pro")

# קבוצות לפי ליגה (כולל ליגות חדשות)
LEAGUE_TEAMS = {
    'Bundesliga': [
        'Augsburg', 'Bayern Munich', 'Bochum', 'Dortmund', 'Ein Frankfurt',
        'Freiburg', 'Heidenheim', 'Hoffenheim', 'Holstein Kiel', 'Leverkusen',
        "M'gladbach", 'Mainz', 'RB Leipzig', 'St Pauli', 'Stuttgart',
        'Union Berlin', 'Werder Bremen', 'Wolfsburg'
    ],
    'Premier League': [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton',
        'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Ipswich',
        'Leicester', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        "Nott'm Forest", 'Southampton', 'Tottenham', 'West Ham', 'Wolves'
    ],
    'La Liga': [
        'Alaves', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis', 'Celta',
        'Espanol', 'Getafe', 'Girona', 'Las Palmas', 'Leganes', 'Mallorca',
        'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad', 'Valencia',
        'Valladolid', 'Vallecano', 'Villarreal'
    ],
    'Ligue 1': [
        'Angers', 'Auxerre', 'Brest', 'Le Havre', 'Lens', 'Lille', 'Lyon',
        'Marseille', 'Monaco', 'Montpellier', 'Nantes', 'Nice', 'Paris SG',
        'Reims', 'Rennes', 'St Etienne', 'Strasbourg', 'Toulouse'
    ],
    'Serie A': [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Empoli', 'Fiorentina',
        'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza',
        'Napoli', 'Parma', 'Roma', 'Torino', 'Udinese', 'Venezia', 'Verona'
    ],
    'Israeli Premier League': [
        'מכבי תל אביב', 'מכבי חיפה', 'הפועל תל אביב', 'הפועל חיפה', 'הפועל באר שבע',
        'בית"ר ירושלים', 'מכבי נתניה', 'הפועל חדרה', 'הפועל ירושלים', 'בני סכנין',
        'מכבי פתח תקווה', 'מועדון ספורט אשדוד', 'מכבי בני ריינה', 'עירוני קריית שמונה', 'עירוני טבריה'
    ],
    'Champions League': [
        'Real Madrid', 'Manchester City', 'Bayern Munich', 'Paris SG', 'Chelsea',
        'Barcelona', 'Liverpool', 'Juventus', 'Atletico Madrid', 'Inter Milan'
    ],
    'Europa League': [
        'Sevilla', 'AS Roma', 'Arsenal', 'Napoli', 'Bayer Leverkusen',
        'West Ham', 'Eintracht Frankfurt', 'Real Betis', 'Feyenoord', 'Lazio'
    ],
    'Conference League': [
        'West Ham', 'Feyenoord', 'Roma', 'AZ Alkmaar', 'Union Berlin',
        'Nice', 'Basel', 'Slavia Prague', 'Partizan', 'Marseille'
    ]
}

# טעינת נתונים אוטומטית מ-GitHub
def load_github_data(github_raw_url):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # רענון נתונים כל שעה
def load_league_data():
    data_sources = {
        "Premier League": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/epl.csv",
        "La Liga": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/laliga.csv",
        "Serie A": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/seriea.csv",
        "Bundesliga": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/bundesliga.csv",
        "Ligue 1": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/ligue1.csv",
        "Israeli Premier League": "https://raw.githubusercontent.com/username/repo/main/israel.csv",
        "Champions League": "https://raw.githubusercontent.com/username/repo/main/champions.csv",
        "Europa League": "https://raw.githubusercontent.com/username/repo/main/europa.csv",
        "Conference League": "https://raw.githubusercontent.com/username/repo/main/conference.csv"
    }
    
    league_data = {}
    for league, url in data_sources.items():
        df = load_github_data(url)
        if df is not None:
            league_data[league] = df
    return league_data

# פונקציות חיזוי משופרות
def calculate_expected_goals(home_team, away_team, df):
    # אם אין נתונים, נחזיר ערכים ברירת מחדל
    if df.empty:
        return 1.5, 1.0
    
    league_avg_home = df['FTHG'].mean()
    league_avg_away = df['FTAG'].mean()
    
    # אם אין משחקים עבור הקבוצה הביתית, נשתמש בממוצע הליגה
    home_attack = league_avg_home
    home_defense = league_avg_away
    if not df[df['HomeTeam'] == home_team].empty:
        home_attack = df[df['HomeTeam'] == home_team]['FTHG'].mean()
        home_defense = df[df['HomeTeam'] == home_team]['FTAG'].mean()
    
    away_attack = league_avg_away
    away_defense = league_avg_home
    if not df[df['AwayTeam'] == away_team].empty:
        away_attack = df[df['AwayTeam'] == away_team]['FTAG'].mean()
        away_defense = df[df['AwayTeam'] == away_team]['FTHG'].mean()
    
    # נרמול לפי ממוצעי הליגה
    home_attack_factor = home_attack / league_avg_home if league_avg_home != 0 else 1.0
    away_defense_factor = away_defense / league_avg_home if league_avg_home != 0 else 1.0
    expected_home_goals = league_avg_home * home_attack_factor * away_defense_factor
    
    away_attack_factor = away_attack / league_avg_away if league_avg_away != 0 else 1.0
    home_defense_factor = home_defense / league_avg_away if league_avg_away != 0 else 1.0
    expected_away_goals = league_avg_away * away_attack_factor * home_defense_factor
    
    return expected_home_goals, expected_away_goals

def predict_match(home_team, away_team, df):
    home_goals, away_goals = calculate_expected_goals(home_team, away_team, df)
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            p = poisson.pmf(i, home_goals) * poisson.pmf(j, away_goals)
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p
                
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

# ממשק משתמש
data = load_league_data()
selected_league = st.selectbox("בחר ליגה", options=list(LEAGUE_TEAMS.keys()))

if selected_league in data and not data[selected_league].empty:
    teams = LEAGUE_TEAMS[selected_league]
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
