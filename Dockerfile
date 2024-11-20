# Use a lightweight Python image
FROM python:3.9-slim

# Set a specific working directory
WORKDIR /app

# Install system dependencies (only if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the app directory into the container
COPY ./app /app

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app \
    JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Expose the application port (FastAPI default is 80)
EXPOSE 80

# Run the FastAPI app
CMD ["python", "-m", "app.main"]