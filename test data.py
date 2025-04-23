import pandas as pd
import random
from datetime import datetime, timedelta

# Generate test data for the last 30 days
today = datetime.utcnow().date()
dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
durations_hours = [round(random.uniform(0, 3), 2) for _ in dates]  # 0 to 3 hours random
durations_seconds = [int(h * 3600) for h in durations_hours]

# Create DataFrame
df = pd.DataFrame({
    "date": [d.isoformat() for d in dates],
    "duration_seconds": durations_seconds
})

# Save to CSV for the bot to use
csv_path = "steam_activity.csv"
df.to_csv(csv_path, index=False)
