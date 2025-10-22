import pandas as pd
import requests
from io import StringIO
from sqlalchemy import create_engine
from database import engine_main, Base_main
from models import RideVendor1, RideVendor2

def run_migration(s3_url: str):
    print("Downloading CSV from S3...")
    response = requests.get(s3_url)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))
    print(f"Loaded CSV with {len(df)} rows")

    # Split data
    df_vendor1 = df[df["vendor_id"] == 1]
    df_vendor2 = df[df["vendor_id"] == 2]

    # Create tables
    Base_main.metadata.drop_all(bind=engine_main)
    Base_main.metadata.create_all(bind=engine_main)

    # Insert data
    print("Inserting data into rides_vendor1...")
    df_vendor1.to_sql("rides_vendor1", engine_main, if_exists="append", index=False)
    print(f"Inserted {len(df_vendor1)} rows into rides_vendor1")

    print("Inserting data into rides_vendor2...")
    df_vendor2.to_sql("rides_vendor2", engine_main, if_exists="append", index=False)
    print(f"Inserted {len(df_vendor2)} rows into rides_vendor2")

    print("Migration completed successfully!")

if __name__ == "__main__":
    S3_CSV_URL = "https://is3.cloudhost.id/rosy/train.csv"
    run_migration(S3_CSV_URL)