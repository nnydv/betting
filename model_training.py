import pandas as pd
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score

# Load cleaned data
df = pd.read_csv("cleaned_matches.csv")

# Feature Engineering
df["home_win"] = df["result"].apply(lambda x: 1 if x == "H" else 0)  # Target variable
features = ["home_goals", "away_goals"]  # Simple features for now

X = df[features]
y = df["home_win"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost
model = xgb.XGBClassifier()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Model Accuracy: {accuracy * 100:.2f}%")

# Save model
model.save_model("model.json")