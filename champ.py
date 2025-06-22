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
st.title("⚽ Football Match Predictor Pro - עונת 2025/2026")

# ----------------------------
# קבוצות לפי ליגה (עונת 2025-2026)
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
        'Burnley', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham',
        'Leeds United', 'Liverpool', 'Man City', 'Man United', 'Newcastle',
        "Nott'm Forest", 'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
    ],
    'La Liga': [
        'Alaves', 'Almeria', 'Ath Bilbao', 'Ath Madrid', 'Barcelona', 'Betis',
        'Cadiz', 'Celta', 'Getafe', 'Girona', 'Las Palmas', 'Leganes',
        'Mallorca', 'Osasuna', 'Real Madrid', 'Sevilla', 'Sociedad',
        'Valencia', 'Valladolid', 'Villarreal'
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
    # ליגת האלופות עונת 2025-2026 (מורחבת)
    'Champions League': [
        'Real Madrid', 'Barcelona', 'Ath Madrid', 'Athletic Bilbao',
        'Bayern Munich', 'Dortmund', 'RB Leipzig', 'Leverkusen', 'Stuttgart',
        'Inter', 'Milan', 'Juventus', 'Atalanta', 'Bologna', 'AC Fiorentina',
        'Man City', 'Arsenal', 'Liverpool', 'Chelsea', 'Aston Villa', 'Newcastle',
        'Paris SG', 'Monaco', 'Lille', 'Brest', 'Lyon',
        'Celtic', 'Rangers', 'PSV', 'Feyenoord', 'Ajax',
        'Benfica', 'Porto', 'Sporting', 'Braga',
        'Shakhtar', 'Dynamo Kyiv',
        'Young Boys', 'Red Star Belgrade', 'Sparta Prague', 'Slavia Prague',
        'Club Brugge', 'Anderlecht', 'Salzburg', 'Sturm Graz',
        'Galatasaray', 'Fenerbahce', 'Besiktas',
        'Bodo/Glimt', 'Molde', 'Copenhagen'
    ],
    # ליגת אירופה עונת 2025-2026 (כולל מהסיבוב הראשון)
    'Europa League': [
        'Man United', 'Tottenham', 'West Ham', 'Brighton', 'Fulham',
        'Roma', 'Lazio', 'Fiorentina', 'Napoli', 'Torino',
        'Ein Frankfurt', 'Hoffenheim', 'Union Berlin', 'Mainz',
        'Lyon', 'Nice', 'Marseille', 'Rennes', 'Strasbourg', 'Lens',
        'Villarreal', 'Betis', 'Sociedad', 'Sevilla', 'Valencia', 'Celta',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Vitesse',
        'Braga', 'Vitoria Guimaraes', 'Rio Ave',
        'Fenerbahce', 'Galatasaray', 'Besiktas', 'Trabzonspor',
        'Olympiacos', 'PAOK', 'AEK Athens', 'Panathinaikos',
        'Qarabag', 'Ludogorets', 'FCSB', 'CFR Cluj',
        'Slavia Prague', 'Viktoria Plzen', 'Sparta Prague',
        'Anderlecht', 'Union SG', 'Gent', 'Club Brugge',
        'Midtjylland', 'Copenhagen', 'Bodo/Glimt', 'Molde',
        'Elfsborg', 'Malmo', 'Hammarby', 'AIK',
        'Sheriff', 'Petrocub', 'Pyunik', 'Ararat-Armenia',
        'Riga FC', 'RFS', 'Flora', 'Levadia',
        'Zalgiris', 'Suduva', 'Dinamo Minsk', 'BATE',
        'Partizan', 'Red Star', 'Vojvodina',
        'Dinamo Zagreb', 'Rijeka', 'Hajduk Split',
        'Maribor', 'Olimpija', 'Mura',
        'Shamrock Rovers', 'Derry City', 'St Patricks'
    ],
    # ליגת הקונפרנס עונת 2025-2026 (מורחבת)
    'Conference League': [
        'Chelsea', 'Brighton', 'Fulham', 'Crystal Palace', 'Brentford',
        'Fiorentina', 'Atalanta', 'Roma', 'Lazio', 'Genoa', 'Empoli',
        'Nice', 'Marseille', 'Rennes', 'Lyon', 'Toulouse', 'Montpellier',
        'Villarreal', 'Betis', 'Valencia', 'Getafe', 'Osasuna',
        'Ein Frankfurt', 'Union Berlin', 'Hoffenheim', 'Freiburg', 'Augsburg',
        'Ajax', 'AZ Alkmaar', 'Twente', 'Utrecht', 'Vitesse', 'Go Ahead Eagles',
        'Celtic', 'Rangers', 'Hearts', 'Aberdeen', 'Hibernian',
        'PAOK', 'Olympiacos', 'AEK Athens', 'Panathinaikos', 'Aris',
        'Astana', 'Petrocub', 'Vikingur', 'TNS',
        'Shamrock Rovers', 'Derry City', 'Celje', 'Olimpija',
        'Cercle Brugge', 'Gent', 'Anderlecht', 'Standard Liege', 'Mechelen',
        'Molde', 'Bodo/Glimt', 'Rosenborg', 'Viking', 'Stromsgodset',
        'Djurgarden', 'Hammarby', 'Elfsborg', 'Hacken', 'Sirius',
        'Heidenheim', 'St Gallen', 'Lugano', 'Basel', 'Zurich',
        'Borac', 'Zrinjski', 'Jagiellonia', 'Legia Warsaw',
        'Rapid Vienna', 'LASK', 'Austria Vienna', 'Sturm Graz',
        'Pafos', 'Omonia', 'APOEL', 'AEL',
        'Maccabi Tel Aviv', 'Maccabi Haifa', 'Hapoel Beer Sheva',
        'Dinamo Tbilisi', 'Torpedo Kutaisi', 'Sabah', 'Zira',
        'Ararat-Armenia', 'Pyunik', 'Alashkert', 'Noah',
        'Ballkani', 'Drita', 'Llapi', 'Prishtina',
        'Partizan', 'Red Star', 'Cukaricki', 'Vojvodina',
        'Dinamo Zagreb', 'Rijeka', 'Hajduk Split', 'Osijek',
        'Maribor', 'Olimpija', 'Mura', 'Domzale',
        'Levski', 'CSKA Sofia', 'Ludogorets', 'Arda',
        'FCSB', 'CFR Cluj', 'Rapid Bucharest', 'Universitatea Craiova',
        'Slovan Bratislava', 'Spartak Trnava', 'Zilina', 'Dunajska Streda',
        'Sparta Prague', 'Slavia Prague', 'Viktoria Plzen', 'Jablonec',
        'Ferencvaros', 'Puskas Academy', 'Debrecen', 'Ujpest',
        'Lechia Gdansk', 'Cracovia', 'Pogon Szczecin', 'Warta Poznan',
        'HJK Helsinki', 'KuPS', 'FC Inter Turku', 'Honka',
        'Flora Tallinn', 'Levadia', 'Kalju', 'Paide',
        'Riga FC', 'Valmiera', 'Liepaja', 'Jelgava'
    ]
}

# נתוני ביצועים של קבוצות אירופיות (מעודכן לעונת 2025-2026)
EUROPEAN_TEAM_STATS = {
    # Champions League - טיר עליון
    'Real Madrid': {'home_goals': 2.9, 'away_goals': 2.3, 'home_conceded': 0.8, 'away_conceded': 1.0, 'strength': 96},
    'Barcelona': {'home_goals': 2.7, 'away_goals': 2.1, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 91},
    'Bayern Munich': {'home_goals': 3.0, 'away_goals': 2.4, 'home_conceded': 0.7, 'away_conceded': 0.9, 'strength': 94},
    'Man City': {'home_goals': 2.8, 'away_goals': 2.2, 'home_conceded': 0.8, 'away_conceded': 1.1, 'strength': 93},
    'Paris SG': {'home_goals': 2.6, 'away_goals': 2.0, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 89},
    'Liverpool': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 88},
    'Inter': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 0.9, 'away_conceded': 1.1, 'strength': 86},
    'Arsenal': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 85},
    'Dortmund': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 84},
    'Chelsea': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 83},
    'Ath Madrid': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 0.7, 'away_conceded': 1.0, 'strength': 82},
    'Milan': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.1, 'away_conceded': 1.3, 'strength': 81},
    'Napoli': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 80},
    'Juventus': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.2, 'strength': 79},
    'Atalanta': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 78},
    'Bologna': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 74},
    'Aston Villa': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 76},
    'Monaco': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 77},
    'Lille': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 73},
    'Brest': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 69},
    'Newcastle': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 74},
    'Stuttgart': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 75},
    'Lyon': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 72},
    'Athletic Bilbao': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 73},
    'AC Fiorentina': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 73},
    
    # קבוצות מהמוקדמות
    'Celtic': {'home_goals': 2.3, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.4, 'strength': 72},
    'Rangers': {'home_goals': 2.1, 'away_goals': 1.3, 'home_conceded': 1.1, 'away_conceded': 1.5, 'strength': 70},
    'PSV': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 75},
    'Feyenoord': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 74},
    'Ajax': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 74},
    'Benfica': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 77},
    'Porto': {'home_goals': 2.3, 'away_goals': 1.7, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 76},
    'Sporting': {'home_goals': 2.5, 'away_goals': 1.9, 'home_conceded': 0.9, 'away_conceded': 1.2, 'strength': 78},
    'Braga': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 73},
    'Shakhtar': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 71},
    'RB Leipzig': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 77},
    'Leverkusen': {'home_goals': 2.4, 'away_goals': 1.8, 'home_conceded': 1.0, 'away_conceded': 1.3, 'strength': 80},
    'Galatasaray': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 74},
    'Fenerbahce': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 73},
    'Bodo/Glimt': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 71},
    
    # Europa League - טיר בינוני
    'Man United': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 75},
    'Tottenham': {'home_goals': 2.2, 'away_goals': 1.6, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76},
    'West Ham': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 71},
    'Roma': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 74},
    'Lazio': {'home_goals': 2.1, 'away_goals': 1.5, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 75},
    'Fiorentina': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 73},
    'Ein Frankfurt': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 74},
    'Hoffenheim': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 70},
    'Union Berlin': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 69},
    'Nice': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 71},
    'Marseille': {'home_goals': 2.0, 'away_goals': 1.4, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 73},
    'Villarreal': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 72},
    'Betis': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 71},
    'Sociedad': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 70},
    'Sevilla': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 68},
    'AZ Alkmaar': {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 72},
    'Twente': {'home_goals': 1.8, 'away_goals': 1.2, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 70},
    
    # Conference League - טיר נמוך יותר
    'Brighton': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 68},
    'Fulham': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 67},
    'Crystal Palace': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 66},
    'Hearts': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 64},
    'Aberdeen': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'PAOK': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.2, 'away_conceded': 1.5, 'strength': 66},
    'Olympiacos': {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.1, 'away_conceded': 1.4, 'strength': 68},
    'AEK Athens': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 65},
    'Panathinaikos': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 64},
    'Molde': {'home_goals': 1.6, 'away_goals': 1.0, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 66},
    'Djurgarden': {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 65},
    'Hammarby': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'Elfsborg': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 62},
    'Heidenheim': {'home_goals': 1.2, 'away_goals': 0.6, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 60},
    'St Gallen': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 61},
    'Lugano': {'home_goals': 1.2, 'away_goals': 0.6, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 59},
    'Genoa': {'home_goals': 1.4, 'away_goals': 0.8, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 63},
    'Empoli': {'home_goals': 1.3, 'away_goals': 0.7, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 62}
}

# הוספת נתונים בסיסיים לקבוצות אחרות
def get_team_stats(team, league_type):
    if team in EUROPEAN_TEAM_STATS:
        return EUROPEAN_TEAM_STATS[team]
    
    # נתונים בסיסיים לפי רמת הליגה
    if league_type == 'Champions League':
        return {'home_goals': 1.9, 'away_goals': 1.3, 'home_conceded': 1.3, 'away_conceded': 1.6, 'strength': 76}
    elif league_type == 'Europa League':
        return {'home_goals': 1.7, 'away_goals': 1.1, 'home_conceded': 1.4, 'away_conceded': 1.7, 'strength': 71}
    else:  # Conference League
        return {'home_goals': 1.5, 'away_goals': 0.9, 'home_conceded': 1.5, 'away_conceded': 1.8, 'strength': 66}

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
        "Premier League": [
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/epl.csv"
        ],
        "La Liga": [
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/laliga.csv"
        ],
        "Serie A": [
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/seriea.csv"
        ],
        "Bundesliga": [
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/bundesliga.csv",
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/bundesliga_2025_2026.csv"
        ],
        "Ligue 1": [
            "https://raw.githubusercontent.com/Sh1503/football-match-predictor/main/ligue1.csv"
        ]
    }
    
    league_data = {}
    for league, urls in data_sources.items():
        combined_df = None
        
        for url in urls:
            df = load_github_data(url)
            if df is not None:
                if combined_df is None:
                    combined_df = df
                else:
                    # שילוב של שני DataFrames
                    combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        if combined_df is not None:
            league_data[league] = combined_df
    
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
    home_advantage = 0.25 if league_type == 'Champions League' else 0.3
    away_disadvantage = 0.15 if league_type == 'Champions League' else 0.2
    
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
    "🇮🇱 ליגת העל הישראלית": ['Israeli Premier League'],
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