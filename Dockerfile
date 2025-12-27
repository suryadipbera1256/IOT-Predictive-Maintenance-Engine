# Base Image
FROM python:3.9-slim

# Set Directory
WORKDIR /app

# Install System Dependencies (CRITICAL for XGBoost)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Files
COPY best_model.pkl . 
COPY app.py .

# Open Port
EXPOSE 5000

# Run Command
CMD ["python", "app.py"]