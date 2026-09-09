import os
import time
from datetime import date
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

# New cache directory because the old CSV files
# do not contain all required GeoJSON fields.
RAW_DATA_DIR = Path(
    "data/raw/usgs_earthquakes_m3_plus_v2"
)
RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# New table for validation before replacing the existing table.
SNOWFLAKE_TABLE = "USGS_EARTHQUAKES_NEW"


def get_earthquakes(starttime, endtime):
    """
    Download earthquake events from USGS in GeoJSON format.
    """

    params = {
        "format": "geojson",
        "starttime": starttime,
        "endtime": endtime,
        "minmagnitude": MIN_MAGNITUDE,
        "limit": LIMIT,
    }

    for attempt in range(1, MAX_RETRIES + 1):

        try:
            response = requests.get(
                USGS_URL,
                params=params,
                timeout=60,
            )

            response.raise_for_status()

            data = response.json()

            rows = []

            for feature in data.get("features", []):

                properties = feature.get(
                    "properties",
                    {},
                )

                geometry = feature.get(
                    "geometry",
                    {},
                ) or {}

                coordinates = geometry.get(
                    "coordinates",
                    [None, None, None],
                )

                longitude = (
                    coordinates[0]
                    if len(coordinates) > 0
                    else None
                )

                latitude = (
                    coordinates[1]
                    if len(coordinates) > 1
                    else None
                )

                depth = (
                    coordinates[2]
                    if len(coordinates) > 2
                    else None
                )

                rows.append(
                    {
                        # Core event fields
                        "id": feature.get("id"),
                        "time": properties.get("time"),
                        "updated": properties.get("updated"),
                        "latitude": latitude,
                        "longitude": longitude,
                        "depth": depth,
                        "mag": properties.get("mag"),
                        "magType": properties.get("magType"),
                        "nst": properties.get("nst"),
                        "gap": properties.get("gap"),
                        "dmin": properties.get("dmin"),
                        "rms": properties.get("rms"),
                        "net": properties.get("net"),
                        "place": properties.get("place"),
                        "type": properties.get("type"),
                        "horizontalError": properties.get(
                            "horizontalError"
                        ),
                        "depthError": properties.get(
                            "depthError"
                        ),
                        "magError": properties.get(
                            "magError"
                        ),
                        "magNst": properties.get("magNst"),
                        "status": properties.get("status"),
                        "locationSource": properties.get(
                            "locationSource"
                        ),
                        "magSource": properties.get(
                            "magSource"
                        ),

                        # Agreed additional fields
                        "mmi": properties.get("mmi"),
                        "cdi": properties.get("cdi"),
                        "felt": properties.get("felt"),
                        "tsunami": properties.get("tsunami"),
                        "alert": properties.get("alert"),
                        "sig": properties.get("sig"),
                        "url": properties.get("url"),
                        "detail": properties.get("detail"),
                        "ids": properties.get("ids"),
                        "types": properties.get("types"),
                        "code": properties.get("code"),
                    }
                )

            return pd.DataFrame(rows)

        except requests.exceptions.RequestException as error:

            print(
                f"Request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(5)
            else:
                raise


def main():

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

            endtime = (
                f"{next_year}-{next_month:02d}-01"
            )

            # Do not request future months.
            if starttime >= date.today().isoformat():
                break

            file_path = (
                RAW_DATA_DIR
                / f"{year}_{month:02d}.csv"
            )

            if file_path.exists():

                print(
                    f"Loading cached data: {starttime}"
                )

                earthquakes_df = pd.read_csv(
                    file_path
                )

            else:

                print(
                    f"Downloading "
                    f"{starttime} → {endtime}"
                )

                earthquakes_df = get_earthquakes(
                    starttime,
                    endtime,
                )

                earthquakes_df.to_csv(
                    file_path,
                    index=False,
                )

                print(
                    f"Downloaded "
                    f"{len(earthquakes_df)} rows"
                )

            earthquake_dataframes.append(
                earthquakes_df
            )

    all_earthquakes_df = pd.concat(
        earthquake_dataframes,
        ignore_index=True,
    )

    # Timestamp of the ingestion into the RAW layer.
    # This is NOT the earthquake event time.
    all_earthquakes_df["_INGESTED_AT"] = (
        pd.Timestamp.now(tz="UTC")
    )

    print()
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

    # ---------------------------------------------------------------
    # Validate required fields before Snowflake upload
    # ---------------------------------------------------------------

    required_columns = {
        "id",
        "time",
        "updated",
        "latitude",
        "longitude",
        "depth",
        "mag",
        "magType",
        "place",
        "type",
        "mmi",
        "cdi",
        "felt",
        "tsunami",
        "alert",
        "sig",
        "url",
        "detail",
        "ids",
        "types",
        "code",
        "_INGESTED_AT",
    }

    missing_columns = (
        required_columns
        - set(all_earthquakes_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    duplicate_count = (
        all_earthquakes_df["id"]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"Found {duplicate_count} duplicate event IDs."
        )

    print()
    print(
        "Required column validation: PASSED"
    )

    print(
        "Duplicate ID validation: PASSED"
    )

    # ---------------------------------------------------------------
    # Snowflake
    # ---------------------------------------------------------------

    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    cursor = connection.cursor()

    try:

        # Remove the temporary NEW table from a previous run.
        # The existing USGS_EARTHQUAKES table remains untouched.
        cursor.execute(
            f"""
            DROP TABLE IF EXISTS
            BLUE_DOT_PLOT.RAW.{SNOWFLAKE_TABLE}
            """
        )

        print()
        print(
            "Uploading to "
            f"BLUE_DOT_PLOT.RAW.{SNOWFLAKE_TABLE}"
        )

        success, number_of_chunks, number_of_rows, output = (
            write_pandas(
                connection,
                all_earthquakes_df,
                SNOWFLAKE_TABLE,
                database="BLUE_DOT_PLOT",
                schema="RAW",
                auto_create_table=True,
                quote_identifiers=False,
                use_logical_type=True,
            )
        )

        print()
        print(
            f"Upload successful: {success}"
        )

        print(
            f"Rows uploaded: {number_of_rows}"
        )

        print(
            f"Number of chunks: {number_of_chunks}"
        )

        if not success:
            raise RuntimeError(
                "Snowflake upload was not successful."
            )

    finally:

        cursor.close()
        connection.close()

        print(
            "Connection closed."
        )


if __name__ == "__main__":
    main()