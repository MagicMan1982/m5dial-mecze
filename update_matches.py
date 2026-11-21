 import json
     from datetime import datetime
     import requests
     from bs4 import BeautifulSoup
    
     def get_team_fixture(url, team_name):
         try:
             headers = {'User-Agent': 'Mozilla/5.0'}
             response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
   
                # Przykładowe wyciąganie najbliższego meczu ze struktury fixtur.es
                # (dopasujemy selektory do dokładnego kodu HTML strony)
                match_row = soup.find('div', class_='fixture-row') # lub odpowiednik na stronie
                if match_row:
                    rival = match_row.find('span', class_='rival-name').text.strip()
                    date = match_row.find('span', class_='match-date').text.strip()
                    return {"team": team_name, "rival": rival, "date": date}
        except Exception as e:
            print(f"Błąd pobierania dla {team_name}: {e}")
   
        # Fallback jeśli pobieranie się nie powiodło
        return {"team": team_name, "rival": "Sprawdź w sieci", "date": "Brak danych"}
   
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
   
        print("Zaktualizowano matches.json z sieci:", datetime.now())
   
    if __name__ == "__main__":
        main()
