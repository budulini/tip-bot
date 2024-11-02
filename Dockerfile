# Use an official Python runtime as a parent image
FROM python:3.13

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies separately
COPY requirements.txt .

# Install any dependencies (caches this layer unless requirements.txt changes)
RUN apt-get update && apt-get install -y ffmpeg libopus-dev

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application
CMD ["python", "tipbot.py"]
