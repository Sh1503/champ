import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO

# ... (הגדרות דף זהות)

# עדכון מילון הליגות והקבוצות
LEAGUE_TEAMS = {
    # ... (ליגות קיימות)
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
    ]
}

# פונקציית טעינת נתונים משופרת
def load_github_data(github_raw_url, required_columns=['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']):
    try:
        response = requests.get(github_raw_url)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        
        # הוספת עמודות חסרות עם ערכי NaN
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

# פונקציות חיזוי משופרות
def calculate_expected_goals(home_team, away_team, df):
    if df.empty or df['FTHG'].isnull().all() or df['FTAG'].isnull().all():
        return 1.5, 1.0  # ערכי ברירת מחדל
    
    # ... (קוד קיים ללא שינוי)

def get_corners_prediction(home_team, away_team, df):
    corner_columns = ['HC', 'AC', 'H.Corners', 'A.Corners', 'CH', 'CA']
    available_columns = [col for col in corner_columns if col in df.columns]
    
    if not available_columns:
        return None
        
    home_corners = df[df['HomeTeam'] == home_team][available_columns[0]].mean()
    away_corners = df[df['AwayTeam'] == away_team][available_columns[1]].mean()
    return round(home_corners + away_corners, 1)

# ... (יתר הקוד ללא שינוי)

# הוספת בדיקות תקינות בממשק
if selected_league in data and not data[selected_league].empty:
    # ... (קוד קיים)
    
    if st.button("חשב חיזוי ⚡"):
        # הודעות אזהרה לפני חישוב
        if data[selected_league]['FTHG'].isnull().all():
            st.warning("⚠️ נתוני שערים חסרים - החיזוי עשוי להיות לא מדויק")
        if 'HC' not in data[selected_league].columns:
            st.warning("⚠️ נתוני קרנות חסרים")
        
        prediction = predict_match(home_team, away_team, data[selected_league])
        # ... (הצגת תוצאות)
