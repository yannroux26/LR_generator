import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv(dotenv_path="openaikey.env")
assert os.getenv("OPENAI_API_KEY"), "OPENAI_API_KEY is not set!"
API_KEY = os.getenv("OPENAI_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

def get_usage(start_date, end_date):
    url = f"https://api.openai.com/v1/dashboard/billing/usage?start_date={start_date}&end_date={end_date}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        usage = data.get("total_usage", 0) / 100  # Convertir en dollars
        print(f"Cost of API usage from {start_date} to {end_date}: {usage} $")
        return round(usage, 2)
    else:
        print("Erreur:", response.status_code, response.text)
        return None

def main():
    today = datetime.utcnow().date()
    start_of_month = today.replace(day=1)
    
    usage = get_usage("2025-05-01", today.isoformat())
    print(f" Date de début du mois : {start_of_month.isoformat()}")

    if usage is not None:
        print(f"💸 Utilisation depuis le {start_of_month} : {usage} $")
        if usage > 20:  # Seuil d’alerte perso
            print("🚨 Attention : vous avez dépassé 20 $ d'utilisation ce mois-ci !")

    else:
        print("❌ Impossible de récupérer les données d'utilisation.")

if __name__ == "__main__":
    main()
