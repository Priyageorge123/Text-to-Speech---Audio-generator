# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg and other system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (Optional, for flexibility)
ENV TTS_URL="https://dfki-3109.dfki.de/tts/run/predict"
ENV FILE_BASE_URL="https://dfki-3109.dfki.de/tts/file="
ENV MAX_CHAR_LIMIT=100

# Run the application
CMD ["python", "app.py"]
