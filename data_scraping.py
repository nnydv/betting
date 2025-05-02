import requests
import pandas as pd

# Download Premier League data
url = "https://www.football-data.co.uk/mmz4281/2324/E0.csv"
response = requests.get(url)

# Save to CSV
with open("matches.csv", "wb") as f:
    f.write(response.content)

print("✅ Data saved as matches.csv!")