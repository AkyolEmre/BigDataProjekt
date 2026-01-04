# CryptoSentiment Analytics - Dockerfile
# Big Data Analytics Final Project

FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Java 21 for Spark)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Java environment for Spark
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python scripts
COPY *.py ./

# Copy HTML files
COPY *.html ./

# Copy JavaScript files
COPY *.js ./

# Create data directory
RUN mkdir -p resources/data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command
CMD ["python", "start_dashboard.py", "--no-browser"]