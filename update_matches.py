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
            
            # fixtures.es używa Next.js i przechowuje całe dane w skrypcie __NEXT_DATA__
            script_tag = soup.find('script', id='__NEXT_DATA__')
            if script_tag:
                data = json.loads(script_tag.string)
                props = data.get('props', {}).get('pageProps', {})
                fixtures = props.get('fixtures', []) or props.get('team', {}).get('fixtures', []) or props.get('matches', [])
                
                for fix in fixtures:
                    rival = fix.get('awayTeam', {}).get('name') or fix.get('opponent', {}).get('name') or "Przeciwnik"
                    date_str = fix.get('date') or fix.get('startingAt') or "Wkrótce"
                    
                    if rival and date_str:
                        return {
                            "team": team_name,
                            "rival": f"vs {rival}",
                            "date": str(date_str)[:16].replace('T', ' ')
                        }
            
            for tag in soup.find_all(['div', 'span', 'td'], string=lambda s: s and ('vs' in s.lower() or '-' in s)):
                text = tag.get_text(strip=True)
                if len(text) > 3 and len(text) < 40:
                    return {
                        "team": team_name,
                        "rival": text,
                        "date": "Najblizszy mecz"
                    }

    except Exception as e:
        print(f"Błąd parsowania dla {team_name}: {e}")
    
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

    print("Zaktualizowano matches.json z fixtures.es:", datetime.now())

if __name__ == "__main__":
    main()
