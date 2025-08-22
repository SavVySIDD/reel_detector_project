import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Paths
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"

os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

def load_raw_data():
    """
    Load and merge all CICIDS2017 raw CSV files into a single DataFrame.
    Place the raw CSV files into data/raw before running this script.
    """
    all_files = [os.path.join(RAW_DATA_DIR, f) for f in os.listdir(RAW_DATA_DIR) if f.endswith(".csv")]
    if not all_files:
        raise FileNotFoundError("No CSV files found in data/raw. Please download CICIDS2017 dataset and place here.")

    dfs = [pd.read_csv(f) for f in all_files]
    df = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(df)} rows from {len(all_files)} files.")
    return df

def preprocess(df):
    """
    Clean, encode, and split dataset.
    """
    # Drop rows with missing values
    df = df.dropna()

    # Rename target column if needed (CICIDS2017 often uses ' Label')
    if " Label" in df.columns:
        df.rename(columns={" Label": "Label"}, inplace=True)

    # Encode labels (Normal -> 0, Attack -> 1..N)
    encoder = LabelEncoder()
    df["Label"] = encoder.fit_transform(df["Label"])

    # Split features/target
    X = df.drop(columns=["Label"])
    y = df["Label"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Save processed files
    train = pd.concat([X_train, y_train], axis=1)
    test = pd.concat([X_test, y_test], axis=1)

    train.to_csv(os.path.join(PROCESSED_DATA_DIR, "train.csv"), index=False)
    test.to_csv(os.path.join(PROCESSED_DATA_DIR, "test.csv"), index=False)

    print(f"Saved processed data: {len(train)} train rows, {len(test)} test rows.")

if __name__ == "__main__":
    df = load_raw_data()
    preprocess(df)
