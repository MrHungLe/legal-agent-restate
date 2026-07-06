FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 9080 for the Restate service endpoint
EXPOSE 9080

CMD ["python", "main.py"]
