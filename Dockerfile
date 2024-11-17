FROM python:3.9-slim

# Set the working directory
WORKDIR /

# Install Java (OpenJDK 17) and other system dependencies
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    && apt-get clean

# Copy the entire app directory into /app
COPY ./app /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add /app to PYTHONPATH
ENV PYTHONPATH=/app

# Set Java's home directory (optional, depending on your application)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Expose the application port
EXPOSE 80

# Run the FastAPI app
CMD ["python", "-m", "app.main"]