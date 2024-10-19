# Use the official Python image
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Install ffmpeg and libopus
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first (for dependency caching)
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot code into the container
COPY . .

# Expose the port for the HTTP server (Flask default is 5000)
EXPOSE 5000

# Set environment variables (optional)
# ENV DISCORD_BOT_TOKEN=<your-bot-token>

# Define the command to run the bot and the HTTP server
CMD ["sh", "-c", "python main.py & python log_server.py"]