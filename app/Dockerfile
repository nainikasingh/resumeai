FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire app directory into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the container port
EXPOSE 80

# Set the Python path to ensure `app` is treated as a module
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "-m", "app.main"]
