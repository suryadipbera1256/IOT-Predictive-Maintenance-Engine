import joblib
import pandas as pd
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. Load the Trained Model
try:
    # Load the entire artifact (which is a dictionary)
    model_artifact = joblib.load('best_model.pkl')
    
    # Check if it's a dictionary (the new "bundled" format)
    if isinstance(model_artifact, dict) and 'model' in model_artifact:
        model = model_artifact['model']
        print("✅ Model loaded successfully (from artifact bundle).")
        
        # Optional: You can also load the optimized threshold if you want to use it
        # threshold = model_artifact.get('threshold', 0.5) 
    else:
        # Fallback for older .pkl files that might just be the model
        model = model_artifact
        print("✅ Model loaded successfully (direct object).")
        
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None

# 2. Helper Function to Format Data
def prepare_input(data_dict):
    """
    Ensures input data has the exact columns and order the model expects.
    """
    # REMOVED 'machine_id' from this list to match training data
    feature_order = [
        'temperature', 'pressure', 'vibration', 
        'temperature_roll_mean', 'pressure_roll_mean', 'vibration_roll_mean'
    ]
    
    # Convert dictionary values to float/int
    # (The list comprehension filters out machine_id if it's sent in the request)
    processed_data = {k: float(v) for k, v in data_dict.items() if k in feature_order}
    
    # Create DataFrame with specific column order
    return pd.DataFrame([processed_data])[feature_order]

# 3. HTML Template for the User Interface
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>FactoryGuard Check</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding-top: 50px; }
        .container { max-width: 800px; }
        .card { border: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .result-box { margin-top: 20px; padding: 15px; border-radius: 5px; text-align: center; }
        .safe { background-color: #d1e7dd; color: #0f5132; }
        .danger { background-color: #f8d7da; color: #842029; }
    </style>
</head>
<body>
<div class="container">
    <div class="card">
        <div class="card-header bg-primary text-white">
            <h3> FactoryGuard AI Tester</h3>
        </div>
        <div class="card-body">
            <form method="POST" action="/">
                
                <h5 class="mb-3">Machine Info</h5>
                <div class="mb-3">
                    <label>Machine ID</label>
                    <input type="number" name="machine_id" class="form-control" value="{{ inputs.machine_id if inputs else '1' }}" required>
                </div>

                <h5 class="mb-3">Current Sensor Readings</h5>
                <div class="row mb-3">
                    <div class="col">
                        <label>Temperature</label>
                        <input type="number" step="0.01" name="temperature" class="form-control" value="{{ inputs.temperature if inputs else '642.35' }}" required>
                    </div>
                    <div class="col">
                        <label>Pressure</label>
                        <input type="number" step="0.01" name="pressure" class="form-control" value="{{ inputs.pressure if inputs else '554.45' }}" required>
                    </div>
                    <div class="col">
                        <label>Vibration</label>
                        <input type="number" step="0.01" name="vibration" class="form-control" value="{{ inputs.vibration if inputs else '522.86' }}" required>
                    </div>
                </div>

                <h5 class="mb-3">Rolling Averages (4h)</h5>
                <div class="row mb-3">
                    <div class="col">
                        <label>Temp (Mean)</label>
                        <input type="number" step="0.01" name="temperature_roll_mean" class="form-control" value="{{ inputs.temperature_roll_mean if inputs else '642.16' }}" required>
                    </div>
                    <div class="col">
                        <label>Pressure (Mean)</label>
                        <input type="number" step="0.01" name="pressure_roll_mean" class="form-control" value="{{ inputs.pressure_roll_mean if inputs else '554.20' }}" required>
                    </div>
                    <div class="col">
                        <label>Vibration (Mean)</label>
                        <input type="number" step="0.01" name="vibration_roll_mean" class="form-control" value="{{ inputs.vibration_roll_mean if inputs else '522.30' }}" required>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary w-100">Predict Status</button>
            </form>

            {% if result %}
            <div class="result-box {{ 'danger' if result.prediction == 1 else 'safe' }}">
                <h4>Status: {{ result.status }}</h4>
                <p>Failure Probability: <strong>{{ result.prob }}</strong></p>
            </div>
            {% endif %}
            
            {% if error %}
            <div class="alert alert-danger mt-3">{{ error }}</div>
            {% endif %}
        </div>
    </div>
</div>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def home():
    """Renders the HTML UI and handles form submissions."""
    result = None
    inputs = None
    error = None

    if request.method == 'POST':
        try:
            if not model:
                raise Exception("Model not loaded.")

            # Capture inputs to repopulate form
            inputs = request.form.to_dict()
            
            # Prepare data for model
            df = prepare_input(inputs)
            
            # Predict
            failure_prob = model.predict_proba(df)[0, 1]
            prediction = 1 if failure_prob >= 0.5 else 0
            
            result = {
                "prediction": prediction,
                "prob": f"{failure_prob:.2%}",
                "status": "CRITICAL RISK " if prediction == 1 else "Healthy ✅"
            }
        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template_string(html_template, result=result, inputs=inputs, error=error)

@app.route('/api/predict', methods=['POST'])
def predict_api():
    """API Endpoint for external scripts."""
    if not model:
        return jsonify({"error": "Model not loaded"}), 500

    try:
        data = request.get_json()
        df = prepare_input(data)
        
        failure_prob = model.predict_proba(df)[0, 1]
        prediction = 1 if failure_prob >= 0.5 else 0
        
        return jsonify({
            "prediction": int(prediction),
            "failure_probability": float(failure_prob),
            "status": "Failure Risk" if prediction == 1 else "Healthy"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("🚀 App running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)