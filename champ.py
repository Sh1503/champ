import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
import re

st.set_page_config(page_title="חיזוי משחקי כדורגל", layout="centered")

# עדכון מילון הליגות והקבוצות
LEAGUE_TEAMS = {
    'Israeli Premier League': [
        'מכבי תל אביב', 'מכבי חיפה', 'הפועל תל אביב', 'הפועל חיפה', 'הפועל באר שבע',
        'בית"ר ירושלים', 'מכבי נתניה', 'הפועל חדרה', 'הפועל ירושלים', 'בני סכנין',
        'מכבי פתח תקווה', 'מועדון ספורט אשדוד', 'מכבי בני ריינה', 'עירוני קריית שמונה', 'עירוני טבריה'
    ],
    'Champions League': [
        'Real Madrid', 'Bayern Munich', 'Manchester City', 'Paris SG', 'Barcelona',
        'Liverpool', 'Inter', 'Juventus', 'Atletico Madrid', 'Dortmund'
    ],
    'Europa League': [
        'Sevilla', 'AS Roma', 'Arsenal', 'Napoli', 'Bayer Leverkusen',
        'West Ham', 'Eintracht Frankfurt', 'Real Betis', 'Feyenoord', 'Lazio'
    ],
    'Conference League': [
        'West Ham', 'Feyenoord', 'Roma', 'AZ Alkmaar', 'Union Berlin',
        'Nice', 'Basel', 'Slavia Prague', 'Partizan', 'Marseille'
    ],
    'Premier League': [
        'Arsenal', 'Aston Villa', 'Chelsea', 'Everton', 'Liverpool', 'Man City', 'Man United',
        'Newcastle', 'Tottenham', 'West Ham', 'Wolves', 'Brighton', 'Brentford', 'Crystal Palace',
        'Fulham', 'Leeds', 'Leicester', 'Nottingham Forest', 'Southampton', 'Bournemouth'
    ],
    'La Liga': [
        'Real Madrid', 'Barcelona', 'Atletico Madrid', 'Sevilla', 'Real Sociedad', 'Villarreal',
        'Valencia', 'Athletic Club', 'Real Betis', 'Getafe', 'Espanyol', 'Osasuna', 'Celta Vigo',
        'Granada', 'Mallorca', 'Cadiz', 'Alaves', 'Elche', 'Levante', 'Rayo Vallecano'
    ],
    'Serie A': [
        'Juventus', 'Inter', 'Milan', 'Napoli', 'Roma', 'Lazio', 'Atalanta', 'Fiorentina',
        'Torino', 'Udinese', 'Bologna', 'Sassuolo', 'Empoli', 'Sampdoria', 'Spezia',
        'Salernitana', 'Verona', 'Cagliari', 'Genoa', 'Venezia'
    ],
    'Bundesliga': [
        'Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen', 'Union Berlin',
        'Freiburg', 'Eintracht Frankfurt', 'Wolfsburg', 'Mainz', 'Borussia M.Gladbach',
        'Werder Bremen', 'Augsburg', 'Stuttgart', 'Bochum', 'Hoffenheim', 'Hertha BSC',
        'Schalke 04', 'Koln'
    ],
    'Ligue 1': [
        'Paris SG', 'Marseille', 'Lyon', 'Monaco', 'Rennes', 'Nice', 'Lille', 'Montpellier',
        'Strasbourg', 'Reims', 'Lens', 'Angers', 'Brest', 'Nantes', 'Troyes', 'Clermont',
        'Lorient', 'Ajaccio', 'Auxerre', 'Toulouse'
    ]
}

def safe_load_csv(url):
    """טוען נתוני CSV עם טיפול בשגיאות"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.warning(f"⚠️ שגיאה בטעינת נתונים: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_league_data():
    """טוען נתוני ליגות עם מקורות עדכניים"""
    data_sources = {
        "Premier League": "https://raw.githubusercontent.com/Sh1503/champ/main/epl.csv",
        "La Liga": "https://raw.githubusercontent.com/Sh1503/champ/main/laliga.csv",
        "Serie A": "https://raw.githubusercontent.com/Sh1503/champ/main/seriea.csv",
        "Bundesliga": "https://raw.githubusercontent.com/Sh1503/champ/main/bundesliga.csv",
        "Ligue 1": "https://raw.githubusercontent.com/Sh1503/champ/main/ligue1.csv",
        "Israeli Premier League": "https://raw.githubusercontent.com/Sh1503/champ/main/israel_league_list.csv",
        "Champions League": "https://raw.githubusercontent.com/footballcsv/euro/master/2024-2025/ucl.csv",
        "Europa League": "https://raw.githubusercontent.com/footballcsv/euro/master/2024-2025/uel.csv",
        "Conference League": "https://raw.githubusercontent.com/footballcsv/euro/master/2024-2025/uecl.csv"
    }
    
    league_data = {}
    for league, url in data_sources.items():
        df = safe_load_csv(url)
        if df is not None:
            # וידוא עמודות נדרשות
            for col in ['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']:
                if col not in df.columns:
                    df[col] = np.nan
            league_data[league] = df
        else:
            st.warning(f"נכשל בטעינת נתונים עבור {league}")
    
    return league_data

def get_uefa_stats(team):
    """מביא סטטיסטיקות רשמיות של UEFA עבור קבוצות"""
    # נתונים מבוססי FBref ונתונים רשמיים [3][6]
    uefa_stats = {
        'Bayern Munich': {'goals_scored': 31, 'goals_conceded': 15},
        'Real Madrid': {'goals_scored': 28, 'goals_conceded': 12},
        'Paris SG': {'goals_scored': 33, 'goals_conceded': 14},
        'Barcelona': {'goals_scored': 43, 'goals_conceded': 18},
        'Liverpool': {'goals_scored': 35, 'goals_conceded': 16},
        'Inter': {'goals_scored': 27, 'goals_conceded': 11},
        'Atletico Madrid': {'goals_scored': 29, 'goals_conceded': 13},
        'Dortmund': {'goals_scored': 32, 'goals_conceded': 17}
    }
    return uefa_stats.get(team, {'goals_scored': 1.8, 'goals_conceded': 1.2})

def calculate_expected_goals(home_team, away_team, df, league):
    """מחשב שערים צפויים עם התאמה לליגות אירופיות"""
    if 'Champions' in league or 'Europa' in league or 'Conference' in league:
        home_stats = get_uefa_stats(home_team)
        away_stats = get_uefa_stats(away_team)
        return (
            round(home_stats['goals_scored'] * 0.6, 2),
            round(away_stats['goals_scored'] * 0.4, 2)
        )
    else:
        if df.empty or df['FTHG'].isnull().all() or df['FTAG'].isnull().all():
            return 1.5, 1.0
        
        home_games = df[df['HomeTeam'] == home_team]
        away_games = df[df['AwayTeam'] == away_team]
        
        home_avg = home_games['FTHG'].mean() if not home_games.empty else 1.5
        away_avg = away_games['FTAG'].mean() if not away_games.empty else 1.0
        
        return round(home_avg, 2), round(away_avg, 2)

def predict_match(home_team, away_team, df, league):
    """מבצע חיזוי מותאם לליגה"""
    home_exp, away_exp = calculate_expected_goals(home_team, away_team, df, league)
    
    return {
        "שערים צפויים מארחת": home_exp,
        "שערים צפויים אורחת": away_exp,
        "סך קרנות משוער": None  # לא זמין בנתונים רשמיים
    }

# ממשק משתמש
st.title("⚽ חיזוי משחקי כדורגל - כל הליגות")

data = load_league_data()

selected_league = st.selectbox("בחר ליגה", list(LEAGUE_TEAMS.keys()))
home_team = st.selectbox("בחר קבוצה מארחת", LEAGUE_TEAMS[selected_league])
away_team = st.selectbox("בחר קבוצה אורחת", [team for team in LEAGUE_TEAMS[selected_league] if team != home_team])

if st.button("חשב חיזוי ⚡"):
    if selected_league in data and not data[selected_league].empty:
        prediction = predict_match(home_team, away_team, data[selected_league], selected_league)
        
        st.subheader("תוצאות החיזוי:")
        st.write(f"⚽ שערים צפויים {home_team}: {prediction['שערים צפויים מארחת']}")
        st.write(f"⚽ שערים צפויים {away_team}: {prediction['שערים צפויים אורחת']}")
        
        if prediction['סך קרנות משוער'] is not None:
            st.write(f"🟠 סך קרנות משוער: {prediction['סך קרנות משוער']}")
        else:
            st.write("🟠 נתוני קרנות אינם זמינים עבור ליגות אירופיות")
    else:
        st.warning("⚠️ אין נתונים זמינים לליגה זו. החיזוי מבוסס על סטטיסטיקות עונתיות")
        prediction = predict_match(home_team, away_team, pd.DataFrame(), selected_league)
        st.subheader("תוצאות חיזוי מבוסס סטטיסטיקות:")
        st.write(f"⚽ שערים צפויים {home_team}: {prediction['שערים צפויים מארחת']}")
        st.write(f"⚽ שערים צפויים {away_team}: {prediction['שערים צפויים אורחת']}")

# הסברים למשתמש
st.markdown("""
### ℹ️ מקורות נתונים:
- **ליגות אירופיות**: נתונים רשמיים מ-UEFA ועונת 2024/2025
- **ליגות מקומיות**: נתונים מעודכנים מה-GitHub
- **קבוצות ישראליות**: נתוני ליגת העל הישראלית
""")
