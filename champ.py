import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO

st.set_page_config(page_title="חיזוי משחקי כדורגל", layout="centered")

# מילון ליגות וקבוצות
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

def load_github_data(github_raw_url, required_columns=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        for col in required_columns:
            if col not in df.columns:
                df[col] = np.nan
        return df
    except Exception as e:
        st.error(f"שגיאה בטעינת נתונים: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def load_league_data():
    data_sources = {
        "Premier League": "https://raw.githubusercontent.com/Sh1503/champ/main/epl.csv",
        "La Liga": "https://raw.githubusercontent.com/Sh1503/champ/main/laliga.csv",
        "Serie A": "https://raw.githubusercontent.com/Sh1503/champ/main/seriea.csv",
        "Bundesliga": "https://raw.githubusercontent.com/Sh1503/champ/main/bundesliga.csv",
        "Ligue 1": "https://raw.githubusercontent.com/Sh1503/champ/main/ligue1.csv",
        "Israeli Premier League": "https://raw.githubusercontent.com/Sh1503/champ/main/israel_league_list.csv",
        "Champions League": "https://www.football-data.co.uk/mmz4281/2324/UCL.csv",
        "Europa League": "https://www.football-data.co.uk/mmz4281/2324/EL.csv",
        "Conference League": "https://www.football-data.co.uk/mmz4281/2324/ECL.csv"
    }
    league_data = {}
    for league, url in data_sources.items():
        df = load_github_data(url)
        if df is not None:
            league_data[league] = df
    return league_data

def calculate_expected_goals(home_team, away_team, df):
    if df.empty or df['FTHG'].isnull().all() or df['FTAG'].isnull().all():
        return 1.5, 1.0
    home_games = df[df['HomeTeam'] == home_team]
    away_games = df[df['AwayTeam'] == away_team]
    home_avg = home_games['FTHG'].mean() if not home_games.empty else 1.5
    away_avg = away_games['FTAG'].mean() if not away_games.empty else 1.0
    return round(home_avg, 2), round(away_avg, 2)

def get_corners_prediction(home_team, away_team, df):
    corner_columns = ['HC', 'AC', 'H.Corners', 'A.Corners', 'CH', 'CA']
    available_columns = [col for col in corner_columns if col in df.columns]
    if not available_columns:
        return None
    home_corners = df[df['HomeTeam'] == home_team][available_columns[0]].mean()
    away_corners = df[df['AwayTeam'] == away_team][available_columns[1]].mean() if len(available_columns) > 1 else 0
    return round((home_corners or 0) + (away_corners or 0), 1)

def predict_match(home_team, away_team, df):
    home_exp, away_exp = calculate_expected_goals(home_team, away_team, df)
    corners = get_corners_prediction(home_team, away_team, df)
    return {
        "שערים צפויים מארחת": home_exp,
        "שערים צפויים אורחת": away_exp,
        "סך קרנות משוער": corners
    }

st.title("⚽ חיזוי משחקי כדורגל - כל הליגות")

data = load_league_data()

selected_league = st.selectbox("בחר ליגה", list(LEAGUE_TEAMS.keys()))
home_team = st.selectbox("בחר קבוצה מארחת", LEAGUE_TEAMS[selected_league])
away_team = st.selectbox("בחר קבוצה אורחת", [team for team in LEAGUE_TEAMS[selected_league] if team != home_team])

if selected_league in data and not data[selected_league].empty:
    if st.button("חשב חיזוי ⚡"):
        if data[selected_league]['FTHG'].isnull().all():
            st.warning("⚠️ נתוני שערים חסרים - החיזוי עשוי להיות לא מדויק")
        if not any(col in data[selected_league].columns for col in ['HC', 'AC', 'H.Corners', 'A.Corners', 'CH', 'CA']):
            st.warning("⚠️ נתוני קרנות חסרים")
        prediction = predict_match(home_team, away_team, data[selected_league])
        st.subheader("תוצאות החיזוי:")
        st.write(f"⚽ שערים צפויים {home_team}: {prediction['שערים צפויים מארחת']}")
        st.write(f"⚽ שערים צפויים {away_team}: {prediction['שערים צפויים אורחת']}")
        if prediction['סך קרנות משוער'] is not None:
            st.write(f"🟠 סך קרנות משוער: {prediction['סך קרנות משוער']}")
        else:
            st.write("🟠 אין נתוני קרנות זמינים למשחק זה.")
else:
    st.error("לא נמצאו נתונים לליגה שנבחרה.")
