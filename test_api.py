import requests
import json

# Define the URL
url = 'http://127.0.0.1:5000/api/predict'

#Define Example Data

sensor_data = {
    "temperature": 642.35,
    "pressure": 554.45,
    "vibration": 522.86,
    "machine_id": 1,  # Added missing feature
    "temperature_roll_mean": 642.16,
    "pressure_roll_mean": 554.20,
    "vibration_roll_mean": 522.30
}

try:
    print(f"Sending data to {url}...")
    response = requests.post(url, json=sensor_data)

    if response.status_code == 200:
        result = response.json()
        print("\n--- ✅ Prediction Success ---")
        print(f"Status: {result['status']}")
        print(f"Failure Probability: {result['failure_probability']:.2%}")
        print(f"Prediction: {result['prediction']}")
    else:
        print(f"\n--- ❌ Error {response.status_code} ---")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n--- ❌ Connection Failed ---")
    print("Ensure app.py is running in a separate terminal.")