import pandas as pd

# Load raw data
df = pd.read_csv("matches.csv")

# Select key columns
df = df[["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]  # FTR = Match Result (H/D/A)
df.columns = ["date", "home_team", "away_team", "home_goals", "away_goals", "result"]

# Save cleaned data
df.to_csv("cleaned_matches.csv", index=False)
print("✅ Data cleaned and saved!")