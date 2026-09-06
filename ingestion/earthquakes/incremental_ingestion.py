import os
from datetime import datetime, timedelta, timezone
from io import StringIO

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


load_dotenv()


USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

MIN_MAGNITUDE = 3
LIMIT = 20000


def get_last_updated(connection):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT MAX(UPDATED)
        FROM BLUE_DOT_PLOT.RAW.USGS_EARTHQUAKES
    """)

    last_updated = cursor.fetchone()[0]

    cursor.close()

    return last_updated


def get_earthquakes(updated_after):

    params = {
        "format": "csv",
        "updatedafter": updated_after,
        "minmagnitude": MIN_MAGNITUDE,
        "limit": LIMIT
    }

    response = requests.get(
        USGS_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return pd.read_csv(
        StringIO(response.text)
    )


connection = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)


last_updated = get_last_updated(connection)

print(f"Last update in Snowflake: {last_updated}")


last_updated_datetime = pd.to_datetime(
    last_updated,
    utc=True
)

updated_after_datetime = (
    last_updated_datetime - timedelta(days=1)
)

updated_after = updated_after_datetime.strftime(
    "%Y-%m-%dT%H:%M:%S"
)

print(f"Requesting USGS data updated after: {updated_after}")


earthquakes_df = get_earthquakes(
    updated_after
)


print(
    f"Rows received from USGS: "
    f"{len(earthquakes_df)}"
)


if earthquakes_df.empty:

    print("No new or updated earthquakes.")

else:

    print(
        f"Unique IDs received: "
        f"{earthquakes_df['id'].nunique()}"
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE OR REPLACE TEMPORARY TABLE
        USGS_EARTHQUAKES_INCREMENTAL
        LIKE BLUE_DOT_PLOT.RAW.USGS_EARTHQUAKES
    """)

    cursor.close()


    success, number_of_chunks, number_of_rows, output = write_pandas(
        connection,
        earthquakes_df,
        "USGS_EARTHQUAKES_INCREMENTAL",
        database="BLUE_DOT_PLOT",
        schema="RAW",
        auto_create_table=False,
        quote_identifiers=False
    )


    print(
        f"Temporary table upload successful: "
        f"{success}"
    )

    print(
        f"Rows uploaded to temporary table: "
        f"{number_of_rows}"
    )


    cursor = connection.cursor()

    cursor.execute("""
        MERGE INTO BLUE_DOT_PLOT.RAW.USGS_EARTHQUAKES AS target

        USING BLUE_DOT_PLOT.RAW.USGS_EARTHQUAKES_INCREMENTAL AS source

        ON target.ID = source.ID

        WHEN MATCHED THEN UPDATE SET
            target.TIME = source.TIME,
            target.LATITUDE = source.LATITUDE,
            target.LONGITUDE = source.LONGITUDE,
            target.DEPTH = source.DEPTH,
            target.MAG = source.MAG,
            target.MAGTYPE = source.MAGTYPE,
            target.NST = source.NST,
            target.GAP = source.GAP,
            target.DMIN = source.DMIN,
            target.RMS = source.RMS,
            target.NET = source.NET,
            target.UPDATED = source.UPDATED,
            target.PLACE = source.PLACE,
            target.TYPE = source.TYPE,
            target.HORIZONTALERROR = source.HORIZONTALERROR,
            target.DEPTHERROR = source.DEPTHERROR,
            target.MAGERROR = source.MAGERROR,
            target.MAGNST = source.MAGNST,
            target.STATUS = source.STATUS,
            target.LOCATIONSOURCE = source.LOCATIONSOURCE,
            target.MAGSOURCE = source.MAGSOURCE

        WHEN NOT MATCHED THEN INSERT (
            TIME,
            LATITUDE,
            LONGITUDE,
            DEPTH,
            MAG,
            MAGTYPE,
            NST,
            GAP,
            DMIN,
            RMS,
            NET,
            ID,
            UPDATED,
            PLACE,
            TYPE,
            HORIZONTALERROR,
            DEPTHERROR,
            MAGERROR,
            MAGNST,
            STATUS,
            LOCATIONSOURCE,
            MAGSOURCE
        )

        VALUES (
            source.TIME,
            source.LATITUDE,
            source.LONGITUDE,
            source.DEPTH,
            source.MAG,
            source.MAGTYPE,
            source.NST,
            source.GAP,
            source.DMIN,
            source.RMS,
            source.NET,
            source.ID,
            source.UPDATED,
            source.PLACE,
            source.TYPE,
            source.HORIZONTALERROR,
            source.DEPTHERROR,
            source.MAGERROR,
            source.MAGNST,
            source.STATUS,
            source.LOCATIONSOURCE,
            source.MAGSOURCE
        )
    """)

    print("MERGE completed successfully.")

    cursor.close()


connection.close()

print("Connection closed.")