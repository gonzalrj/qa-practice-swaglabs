# Dockerfile
FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install chromium and supporting libs and pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      chromium \
      chromium-driver \
      wget \
      unzip \
      gnupg \
      libnss3 \
      libxss1 \
      libasound2 \
      fonts-liberation \
      libatk1.0-0 \
      libcups2 \
      libx11-xcb1 \
      libxcomposite1 \
      libxdamage1 \
      libxrandr2 \
      libgbm1 \
      xdg-utils \
      python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Expose locations for your conftest to pick up if needed
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
# Default: don't set SELENIUM_REMOTE_URL so the image can run locally by default
ENV HEADLESS=true

# Install Python deps
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip && python3 -m pip install --no-cache-dir -r requirements.txt

# Copy project files, entrypoint
COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD []