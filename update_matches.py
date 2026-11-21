import json
from datetime import datetime
    
data = {
  "matches": [
    {"team": "FC Barcelona", "rival": "vs Villarreal", "date": "Niedziela 14:00"},
    {"team": "Radomiak Radom", "rival": "vs Wisla Krakow", "date": "Dzisiaj 20:15"},
    {"team": "Polska", "rival": "Przerwa zimowa", "date": "Kolejny w Marcu"}
  ]
}
   
with open("matches.json", "w", encoding="utf-8") as f:
  json.dump(data, f, ensure_ascii=False, indent=2)
   
  print("Zaktualizowano matches.json:", datetime.now())
