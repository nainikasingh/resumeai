FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the app directory into /app/app
COPY ./app /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Add the /app directory to PYTHONPATH
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 80

# Run the FastAPI app
CMD ["python", "-m", "main"]
