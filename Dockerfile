FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

# Copy runner
COPY runner.py .

CMD ["python", "runner.py"]
