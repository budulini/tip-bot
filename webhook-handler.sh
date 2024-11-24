#!/bin/bash

# Navigate to the project directory
cd /home/janko/tip-bot || exit

# Pull the latest changes
git reset --hard HEAD
git pull origin main

# Optionally restart your application (e.g., for Node.js apps)
# systemctl restart your-app-service

docker compose down
docker compose up -d
