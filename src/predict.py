import joblib
import argparse

# 1. Load trained model
model = joblib.load("models/reel_detector.pkl")

def predict_reel_category(features):
    """
    Predicts the category of a reel given feature input.
    features: list/array of numeric features
    """
    prediction = model.predict([features])
    return prediction[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict reel category")
    parser.add_argument("--features", nargs="+", type=float, required=True,
                        help="Input features separated by space (numeric values)")
    
    args = parser.parse_args()
    
    # Convert list of strings to float list
    input_features = args.features
    predicted_class = predict_reel_category(input_features)
    
    print(f"Predicted Reel Category: {predicted_class}")
