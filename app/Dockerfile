FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the app directory into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Python path to recognize `app` as a module
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 80

# Run the application
CMD ["python", "main.py"]
