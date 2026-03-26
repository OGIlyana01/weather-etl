import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

# EXTRACT
url = "https://api.open-meteo.com/v1/forecast"
params = {
  "latitude": 33.70, "longitude": -117.80,
  "hourly": "temperature_2m,precipitation,windspeed_10m",
  "forecast_days": 7
}
response = requests.get(url, params=params)
data = response.json()["hourly"]

# TRANSFORM
df = pd.DataFrame(data)
df.rename(columns={
  "time": "recorded_at",
  "temperature_2m": "temp_celsius",
  "windspeed_10m": "wind_speed"
}, inplace=True)
df["recorded_at"] = pd.to_datetime(df["recorded_at"])
df.dropna(inplace=True)
df.drop_duplicates(subset=["recorded_at"], inplace=True)
df["ingested_at"] = datetime.utcnow()

# LOAD
engine = create_engine("postgresql://user:password@localhost:5432/weather_db")

with engine.connect() as conn:
  conn.execute(text("""
    CREATE TABLE IF NOT EXISTS weather_hourly (
      recorded_at TIMESTAMP PRIMARY KEY,
      temp_celsius FLOAT,
      precipitation FLOAT,
      wind_speed FLOAT,
      ingested_at TIMESTAMP
    )
  """))
  conn.commit()

df.to_sql("weather_hourly", engine,
  if_exists="replace", index=False, method="multi")

print(f"+-+ Loaded {len(df)} rows at {datetime.utcnow()}")

# Window function
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT recorded_at, temp_celsius,
            LAG(temp_celsius) OVER (ORDER BY recorded_at) AS prev_temp,
            temp_celsius - LAG(temp_celsius) OVER (ORDER BY recorded_at) AS temp_delta
        FROM weather_hourly
        WHERE recorded_at >= NOW() - INTERVAL '7 days'
        ORDER BY recorded_at
    """))
    for row in result:
        print(row)