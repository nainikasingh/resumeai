FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy all contents of the app directory to /app inside the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH to include /app
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 80

# Start the FastAPI app
CMD ["python", "-m", "main"]
