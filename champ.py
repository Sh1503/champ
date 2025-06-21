import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
import requests
from io import StringIO

# הגדרות דף
st.set_page_config(
    page_title="Football Predictor Pro",
    page_icon="⚽",
    layout="centered"
)
st.title("⚽ Football Match Predictor Pro")

# ----------------------------
# קבוצות לפי ליגה (כולל ליגות אירופיות)
# ----------------------------
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
    # ליגות אירופיות - קבוצות מובילות שמשתתפות בדרך כלל
    'Champions League': [
        'Real Madrid', 'Barcelona', 'Bayern Munich', 'Man City', 'Paris SG',
        'Liverpool', 'Chelsea', 'Inter', 'Milan', 'Juventus', 'Dortmund',
        'Arsenal', 'Ath Madrid', 'Napoli', 'Benfica', 'Porto', 'Ajax',
        'PSV', 'Celtic', 'Rangers', 'Shakhtar', 'RB Leipzig', 'Leverkusen',
        'Atalanta', 'Roma', 'Lazio', 'Fiorentina', 'Aston Villa', 'Newcastle',
        'Tottenham', 'West Ham'
    ],
    'Europa League': [
        'Sevilla', 'Arsenal', 'Chelsea', 'Man United', 'Tottenham', 'West Ham',
        'Roma', 'Lazio', 'Napoli', 'Atalanta', 'Fiorentina', 'Ein Frankfurt',
        'Leverkusen', 'Dortmund', 'Lyon', 'Marseille', 'Nice', 'Monaco',
        'Villarreal', 'Betis', 'Sociedad', 'Ath Bilbao', 'Valencia',
        'Ajax', 'PSV', 'Feyenoord', 'Rangers', 'Celtic', 'Benfica', 'Porto',
        'Sporting', 'Braga'
    ],
    'Conference League': [
        'West Ham', 'Fiorentina', 'Roma', 'Atalanta', 'Nice', 'Marseille',
        'Rennes', 'Lyon', 'Toulouse', 'Villarreal', 'Betis', 'Valencia',
        'Espanol', 'Ein Frankfurt', 'Union Berlin', 'Hoffenheim', 'Freiburg',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Vitesse', 'Celtic',
        'Rangers', 'Hearts', 'Aberdeen', 'PAOK', 'Olympiacos', 'AEK Athens'
    ]
}

# נתוני ביצועים של קבוצות אירופיות (מבוסס על עונות קודמות ודירוגים)
EUROPEAN_TEAM_STATS = {
    # Champions League - ממוצעי שערים וחוזק יחסי
    'Real Madrid': {'home_goals': 2.8, 'away_goals': 2.2, 'home_conceded': 0.9, 'away_conceded': 1.1, 'strength': 95},
    'Barcelona': {'home_goals': 2.6, 'away_goals': 2.0, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 90},
    'Bayern Munich': {'home_goals': 2.9, 'away_goals': 2.3, 'home_conceded': 0.8, 'away_conceded': 1.0, 'strength': 93},
    'Man City': {'home_goals': 2.7, 'away_goals': 2.1, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 92},
    'Paris SG': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 88},
    'Liverpool': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 87},
    'Chelsea': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 82},
    'Inter': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.0, 'away_conceded': 1.2, 'strength': 85},
    'Milan': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.2, 'away_conceded': 1.4, 'strength': 80},
    'Juventus': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.1, 'away_conceded': 1.3, 'strength': 78},
    'Dortmund': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 83},
    'Arsenal': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 84},
    'Ath Madrid': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 0.8, 'away_conceded': 1.1, 'strength': 81},
    'Napoli': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 79}
}

# הוספת נתונים בסיסיים לקבוצות אחרות
def get_team_stats(team, league_type):
    if team in EUROPEAN_TEAM_STATS:
        return EUROPEAN_TEAM_STATS[team]
    
    # נתונים בסיסיים לפי רמת הליגה
    if league_type == 'Champions League':
        return {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 75}
    elif league_type == 'Europa League':
        return {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 70}
    else:  # Conference League
        return {'home_goals': 1.4, 'away_goals': 0.9, 'home_conceded': 1.6, 'away_conceded': 1.9, 'strength': 65}

# ----------------------------
# טעינת נתונים אוטומטית מ-GitHub
# ----------------------------
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
        "Ligue 1": "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/ligue1.csv"
    }
    
    league_data = {}
    for league, url in data_sources.items():
        df = load_github_data(url)
        if df is not None:
            league_data[league] = df
    return league_data

# ----------------------------
# פונקציות חיזוי - ליגות רגילות
# ----------------------------
def predict_match_regular(home_team, away_team, df):
    # חישוב ממוצעי שערים
    home_goals = df[df['HomeTeam'] == home_team]['FTHG'].mean()
    away_goals = df[df['AwayTeam'] == away_team]['FTAG'].mean()
    
    # חישוב הסתברויות פואסון
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

# ----------------------------
# פונקציות חיזוי - ליגות אירופיות
# ----------------------------
def predict_match_european(home_team, away_team, league_type):
    home_stats = get_team_stats(home_team, league_type)
    away_stats = get_team_stats(away_team, league_type)
    
    # חישוב שערים צפויים עם התחשבות בחוזק היחסי
    strength_factor = home_stats['strength'] / away_stats['strength']
    
    # התאמת יתרון הבית לליגות אירופיות (יותר מאוזן)
    home_goals_expected = home_stats['home_goals'] * (1 + (strength_factor - 1) * 0.3)
    away_goals_expected = away_stats['away_goals'] * (1 + (1/strength_factor - 1) * 0.2)
    
    # חישוב הסתברויות פואסון
    max_goals = 5
    home_win = draw = away_win = 0.0
    
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            p = poisson.pmf(i, home_goals_expected) * poisson.pmf(j, away_goals_expected)
            if i > j: home_win += p
            elif i == j: draw += p
            else: away_win += p
    
    # חישוב קרנות משוער (בהתבסס על סגנון משחק)
    corners_home = 5.5 + (home_stats['strength'] - 75) * 0.05
    corners_away = 4.5 + (away_stats['strength'] - 75) * 0.03
    
    return {
        "home_win": round(home_win, 3),
        "draw": round(draw, 3),
        "away_win": round(away_win, 3),
        "total_goals": round(home_goals_expected + away_goals_expected, 1),
        "total_corners": round(corners_home + corners_away, 1)
    }

def get_corners_prediction(home_team, away_team, df):
    if 'HC' in df.columns and 'AC' in df.columns:
        home_corners = df[df['HomeTeam'] == home_team]['HC'].mean()
        away_corners = df[df['AwayTeam'] == away_team]['AC'].mean()
        return round(home_corners + away_corners, 1)
    return None

# ----------------------------
# פונקציה מאוחדת לחיזוי
# ----------------------------
def predict_match(home_team, away_team, league, df=None):
    if league in ['Champions League', 'Europa League', 'Conference League']:
        return predict_match_european(home_team, away_team, league)
    else:
        return predict_match_regular(home_team, away_team, df)

# ----------------------------
# ממשק משתמש
# ----------------------------
data = load_league_data()

# קיבוץ הליגות לתצוגה נוחה
league_categories = {
    "🏆 ליגות אירופיות": ['Champions League', 'Europa League', 'Conference League'],
    "🇪🇺 ליגות מקומיות": ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
}

# בחירת קטגוריה וליגה
selected_category = st.selectbox("בחר קטגוריה", options=list(league_categories.keys()))
available_leagues = league_categories[selected_category]
selected_league = st.selectbox("בחר ליגה", options=available_leagues)

if selected_league in LEAGUE_TEAMS:
    teams = LEAGUE_TEAMS[selected_league]
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox("קבוצה ביתית", options=teams)
    
    with col2:
        away_team = st.selectbox("קבוצה אורחת", options=[t for t in teams if t != home_team])
    
    if st.button("חשב חיזוי ⚡", type="primary"):
        # בחירת פונקציית חיזוי מתאימה
        if selected_league in ['Champions League', 'Europa League', 'Conference League']:
            prediction = predict_match(home_team, away_team, selected_league)
            st.info("🌟 חיזוי מבוסס על ביצועים אירופיים ודירוגי קבוצות")
        elif selected_league in data and not data[selected_league].empty:
            prediction = predict_match(home_team, away_team, selected_league, data[selected_league])
            st.info("📊 חיזוי מבוסס על נתונים היסטוריים של הליגה")
        else:
            st.error("לא נמצאו נתונים עבור הליגה הנבחרת")
            st.stop()
        
        # הצגת תוצאות
        st.subheader("🔮 תוצאות חיזוי:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label=f"🏠 ניצחון ל־{home_team}", 
                value=f"{prediction['home_win']*100:.1f}%",
                delta=f"{prediction['home_win']*100 - 33.3:.1f}%" if prediction['home_win']*100 > 33.3 else None
            )
        with col2:
            st.metric(
                label="🤝 תיקו", 
                value=f"{prediction['draw']*100:.1f}%",
                delta=f"{prediction['draw']*100 - 33.3:.1f}%" if prediction['draw']*100 > 33.3 else None
            )
        with col3:
            st.metric(
                label=f"✈️ ניצחון ל־{away_team}", 
                value=f"{prediction['away_win']*100:.1f}%",
                delta=f"{prediction['away_win']*100 - 33.3:.1f}%" if prediction['away_win']*100 > 33.3 else None
            )
        
        st.divider()
        
        # סטטיסטיקות נוספות
        st.subheader("📊 סטטיסטיקות נוספות")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("⚽ שערים צפויים", f"{prediction['total_goals']}")
        
        with col2:
            if prediction['total_corners'] is not None:
                st.metric("🚩 קרנות צפויות", f"{prediction['total_corners']}")
            else:
                st.metric("🚩 קרנות צפויות", "לא זמין")
        
        # המלצות הימור
        st.subheader("💡 המלצות")
        max_prob = max(prediction['home_win'], prediction['draw'], prediction['away_win'])
        
        if max_prob == prediction['home_win']:
            st.success(f"🏠 ההימור המומלץ: ניצחון ל־{home_team} ({prediction['home_win']*100:.1f}%)")
        elif max_prob == prediction['draw']:
            st.success(f"🤝 ההימור המומלץ: תיקו ({prediction['draw']*100:.1f}%)")
        else:
            st.success(f"✈️ ההימור המומלץ: ניצחון ל־{away_team} ({prediction['away_win']*100:.1f}%)")
        
        # המלצות נוספות
        if prediction['total_goals'] > 2.5:
            st.info(f"⚽ משחק עתיר שערים - המלצה: מעל 2.5 שערים ({prediction['total_goals']} צפוי)")
        else:
            st.info(f"🛡️ משחק דחוס - המלצה: מתחת ל-2.5 שערים ({prediction['total_goals']} צפוי)")

else:
    st.error("שגיאה בטעינת נתוני הליגה")

# מידע נוסף
with st.expander("ℹ️ מידע על השיטה"):
    st.markdown("""
    **ליגות מקומיות**: החיזוי מבוסס על נתונים היסטוריים אמיתיים של המשחקים באמצעות התפלגות פואסון.
    
    **ליגות אירופיות**: החיזוי מבוסס על:
    - ביצועים היסטוריים של הקבוצות בתחרויות אירופיות
    - דירוג חוזק יחסי של הקבוצות
    - התאמה לרמת התחרות הגבוהה יותר
    - יתרון בית מופחת (מאחר שמדובר במשחקים בינלאומיים)
    
    **שיטת החישוב**: התפלגות פואסון למשחקי כדורגל עם התאמות לפי סוג הליגה.
    """)

st.markdown("---")
st.markdown("*נבנה עם ❤️ לחובבי כדורגל*")