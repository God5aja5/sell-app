FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget unzip curl gnupg \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Chrome
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copy project files
WORKDIR /app
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render uses PORT env)
EXPOSE 5000

# Start Gunicorn using shell form so $PORT expands
CMD gunicorn app:app --bind 0.0.0.0:$PORT
