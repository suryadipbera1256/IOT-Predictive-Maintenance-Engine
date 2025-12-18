import joblib
import pandas as pd
from flask import Flask, request, jsonify

# 1. Initialize Flask App
app = Flask(__name__)

# 2. Load the Trained Model
try:
    model = joblib.load('best_model.pkl')
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "model_loaded": model is not None})

@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts JSON input with machine sensor data.
    Expected features must match the training set exactly.
    """
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        # Get JSON data
        data = request.get_json()
        
        # Convert to DataFrame (XGBoost expects feature names)
        # Note: In a real production scenario, you would calculate lags here.
        # For this assignment, we assume the input JSON contains the full feature vector.
        input_data = pd.DataFrame([data])
        
        # Make Prediction
        # [:, 1] gets the probability of class 1 (Failure)
        failure_prob = model.predict_proba(input_data)[0, 1]
        
        # Determine status based on your threshold (e.g., 0.60)
        threshold = 0.60
        prediction = 1 if failure_prob >= threshold else 0
        status = "Failure Risk" if prediction == 1 else "Healthy"

        # Generate simplified explanation (Simulating SHAP for API speed)
        # In full production, you would run the SHAP explainer here too.
        
        return jsonify({
            "prediction": int(prediction),
            "failure_probability": float(round(failure_prob, 4)),
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 3. Run the App
if __name__ == '__main__':
    app.run(debug=True, port=5000)