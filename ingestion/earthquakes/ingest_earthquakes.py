import os
import time
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


load_dotenv()


USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

START_YEAR = 2006
END_YEAR = 2026

MIN_MAGNITUDE = 3

LIMIT = 20000
MAX_RETRIES = 5

RAW_DATA_DIR = Path("data/raw/usgs_earthquakes_m3_plus")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_earthquakes(starttime, endtime):

    params = {
        "format": "csv",
        "starttime": starttime,
        "endtime": endtime,
        "minmagnitude": MIN_MAGNITUDE,
        "limit": LIMIT
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = requests.get(
                USGS_URL,
                params=params,
                timeout=60
            )

            response.raise_for_status()

            return pd.read_csv(
                StringIO(response.text)
            )

        except requests.exceptions.RequestException as error:

            print(
                f"Request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(5)
            else:
                raise


earthquake_dataframes = []


for year in range(START_YEAR, END_YEAR + 1):

    for month in range(1, 13):

        starttime = f"{year}-{month:02d}-01"

        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1

        endtime = f"{next_year}-{next_month:02d}-01"

        if starttime >= date.today().isoformat():
            break

        file_path = RAW_DATA_DIR / f"{year}_{month:02d}.csv"

        if file_path.exists():

            print(f"Already downloaded: {starttime}")

            earthquakes_df = pd.read_csv(file_path)

        else:

            print(
                f"Downloading {starttime} → {endtime}"
            )

            earthquakes_df = get_earthquakes(
                starttime,
                endtime
            )

            earthquakes_df.to_csv(
                file_path,
                index=False
            )

            print(
                f"Downloaded and saved "
                f"{len(earthquakes_df)} rows"
            )

        earthquake_dataframes.append(
            earthquakes_df
        )


all_earthquakes_df = pd.concat(
    earthquake_dataframes,
    ignore_index=True
)


print(
    f"Total rows: "
    f"{len(all_earthquakes_df)}"
)

print(
    f"Unique IDs: "
    f"{all_earthquakes_df['id'].nunique()}"
)

print(
    f"Duplicate IDs: "
    f"{all_earthquakes_df['id'].duplicated().sum()}"
)


connection = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)


success, number_of_chunks, number_of_rows, output = write_pandas(
    connection,
    all_earthquakes_df,
    "USGS_EARTHQUAKES",
    database="BLUE_DOT_PLOT",
    schema="RAW",
    auto_create_table=True,
    quote_identifiers=False
)


print(f"Upload successful: {success}")
print(f"Rows uploaded: {number_of_rows}")


connection.close()