import requests
import json

# 1. Define the URL
url = 'http://127.0.0.1:5000/predict'

# 2. Define Example Data (Simulating a sensor reading)
# Ideally, this machine looks healthy (low vibration, stable pressure)
sensor_data = {
    "vibration": 1450,
    "pressure": 55.2,
    "temperature": 310.5,
    "tool_wear": 120,
    # Lag features required by the model
    "vibration_lag_1h": 1440,
    "vibration_lag_2h": 1430,
    "pressure_lag_1h": 54.0,
    "pressure_lag_2h": 53.5,
    "temperature_lag_1h": 310.0,
    "temperature_lag_2h": 309.8
}

try:
    # 3. Send the POST request
    print(f"Sending data to {url}...")
    response = requests.post(url, json=sensor_data)

    # 4. Check the results
    if response.status_code == 200:
        result = response.json()
        print("\n--- ✅ Prediction Success ---")
        print(f"Status: {result['status']}")
        print(f"Failure Probability: {result['failure_probability']:.2%}")
        print(f"Raw Prediction: {result['prediction']}")
    else:
        print(f"\n--- ❌ Error {response.status_code} ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- ❌ Connection Failed ---")
    print("Is the Flask server running? Open a separate terminal and run 'python app.py'")