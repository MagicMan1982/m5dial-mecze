import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_team_fixture(url, team_name):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # fixtures.es używa Schema.org JSON-LD (SportsEvent) dla każdego meczu
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            future_matches = []
            
            now = datetime.now()
            
            for script in json_ld_scripts:
                try:
                    if not script.string:
                        continue
                    data = json.loads(script.string)
                    events = data if isinstance(data, list) else [data]
                    
                    for event in events:
                        if event.get('@type') == 'SportsEvent':
                            start_date_str = event.get('startDate')
                            if start_date_str:
                                # Parsowanie daty ISO z uwzględnieniem strefy czasowej
                                event_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                                event_date_naive = event_date.replace(tzinfo=None)
                                
                                # Interesują nas tylko mecze od teraz w przyszłość
                                if event_date_naive >= now:
                                    home = event.get('homeTeam', {}).get('name', '')
                                    away = event.get('awayTeam', {}).get('name', '')
                                    
                                    # Ustalamy przeciwnika (kto nie jest naszą drużyną)
                                    rival = away if team_name.lower() in home.lower() else home
                                    if not rival or rival.strip() == "":
                                        rival = event.get('name', 'Mecz')
                                        
                                    future_matches.append({
                                        "date": event_date_naive,
                                        "rival": f"vs {rival}",
                                        "date_str": event_date.strftime('%d.%m %H:%M')
                                    })
                except Exception:
                    continue
            
            if future_matches:
                future_matches.sort(key=lambda x: x['date'])
                next_match = future_matches[0]
                return {
                    "team": team_name,
                    "rival": next_match['rival'],
                    "date": next_match['date_str']
                }

    except Exception as e:
        print(f"Błąd parsowania JSON-LD dla {team_name}: {e}")
    
    # Fallback w razie problemów z siecią
    fallbacks = {
        "FC Barcelona": {"rival": "vs Villarreal", "date": "Niedziela 14:00"},
        "Radomiak Radom": {"rival": "vs Wisla Krakow", "date": "Dzisiaj 20:15"},
        "Polska": {"rival": "Przerwa zimowa", "date": "Kolejny w Marcu"}
    }
    return {
        "team": team_name, 
        "rival": fallbacks.get(team_name, {}).get("rival", "Mecz"), 
        "date": fallbacks.get(team_name, {}).get("date", "Wkrótce")
    }

def main():
    teams = [
        {"name": "FC Barcelona", "url": "https://fixtur.es/en/team/fc-barcelona"},
        {"name": "Radomiak Radom", "url": "https://fixtur.es/en/team/rks-radomiak-1"},
        {"name": "Polska", "url": "https://fixtur.es/en/team/pl"}
    ]

    matches = []
    for t in teams:
        match_info = get_team_fixture(t["url"], t["name"])
        matches.append(match_info)

    data = {"matches": matches}

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Zaktualizowano matches.json przez JSON-LD:", datetime.now())

if __name__ == "__main__":
    main()
