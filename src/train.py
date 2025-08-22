import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# Paths
train_path = "data/processed/train.csv"
test_path = "data/processed/test.csv"
model_path = "models/reel_detector.pkl"

# Load data
print("Loading processed data...")
train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

X_train = train_df.drop("Label", axis=1)
y_train = train_df["Label"]

X_test = test_df.drop("Label", axis=1)
y_test = test_df["Label"]

# Clean the data (handle NaN and infinity)
X_train = X_train.replace([float('inf'), -float('inf')], float('nan'))
X_test = X_test.replace([float('inf'), -float('inf')], float('nan'))

# Fill NaN with column means (or 0 if you prefer)
X_train = X_train.fillna(X_train.mean())
X_test = X_test.fillna(X_test.mean())


# Train model
print("Training RandomForest model...")
clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
clf.fit(X_train, y_train)

# Evaluate
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model
os.makedirs("models", exist_ok=True)
joblib.dump(clf, model_path)
print(f"Model saved to {model_path}")
