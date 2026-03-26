# Weather ETL Pipeline

End-to-end ETL pipeline that pulls hourly weather data 
from Open-Meteo API, transforms it with Python/pandas, 
and loads it into PostgreSQL.

## Stack
- Python (requests, pandas, SQLAlchemy)
- PostgreSQL
- Docker

## How to run
1. docker-compose up -d
2. python3 etl.py

## Architecture
API → Python/pandas → PostgreSQL