FROM python:3.11-slim

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "valentine_bot.py"]