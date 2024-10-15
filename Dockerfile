# Use the official Python image from the Docker Hub
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first (for dependency caching)
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot code into the container
COPY . .

# Set environment variables (optional, you can also pass these at runtime)
# ENV DISCORD_BOT_TOKEN=<your-bot-token>

# Define the command to run the bot
CMD ["python", "main.py"]