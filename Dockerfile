FROM n8nio/n8n:latest

USER root

# Install Python 3.12 and dependencies
RUN apk add --no-cache \
    python3=~3.12 \
    py3-pip \
    chromium \
    chromium-chromedriver \
    build-base \
    gcc \
    musl-dev \
    && ln -sf python3 /usr/bin/python

# Set Chrome environment variables
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_PATH=/usr/lib/chromium/

# Install Node.js packages for n8n
RUN npm install -g cheerio

# Switch to node user and install cheerio locally for n8n
USER node
WORKDIR /home/node
RUN npm install cheerio

# Switch back to root for remaining setup
USER root

# Copy requirements and install Python packages
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir --break-system-packages -r /app/requirements.txt

# Copy crawler script
COPY yellowpages_full_crawler.py /app/

# Create output directory
RUN mkdir -p /app/output && chown -R node:node /app

USER node

WORKDIR /home/node