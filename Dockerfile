# 1. Base Image: Start with a lightweight version of Python
FROM python:3.9-slim

# 2. Set Directory: Create a working directory inside the container
WORKDIR /app

# 3. Install Dependencies: Copy requirements and install them
# We copy this first to leverage Docker's cache mechanism
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy Files: Move your code and model into the container
COPY app.py .
COPY best_model.pkl .

# 5. Open Port: Tell Docker this container listens on port 5000
EXPOSE 5000

# 6. Run Command: What happens when the container starts?
CMD ["python", "app.py"]