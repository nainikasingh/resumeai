FROM python:3.9-slim

# Set the working directory to the root of the container
WORKDIR /

# Copy the entire app directory into /app
COPY ./app /app

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add /app to PYTHONPATH
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 80

# Run the FastAPI app
CMD ["python", "-m", "app.main"]
