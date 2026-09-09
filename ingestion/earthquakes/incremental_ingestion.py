import os
import time
from datetime import timedelta

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


load_dotenv()


USGS_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

MIN_MAGNITUDE = 3
LIMIT = 20000
MAX_RETRIES = 5


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
        "format": "geojson",
        "updatedafter": updated_after,
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

                        # These fields are not provided by the
                        # current USGS GeoJSON response.
                        "locationSource": None,
                        "magSource": None,

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


connection = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)


try:

    last_updated = get_last_updated(connection)

    print(
        f"Last update in Snowflake: "
        f"{last_updated}"
    )

    if last_updated is None:
        raise RuntimeError(
            "Could not find the latest UPDATED timestamp "
            "in RAW.USGS_EARTHQUAKES."
        )

    # USGS UPDATED is stored as Unix timestamp in milliseconds.
    last_updated_datetime = pd.to_datetime(
        last_updated,
        unit="ms",
        utc=True,
    )

    # Request one day of overlap to catch events
    # that were updated recently.
    updated_after_datetime = (
        last_updated_datetime
        - timedelta(days=1)
    )

    updated_after = (
        updated_after_datetime.strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
    )

    print(
        f"Requesting USGS data updated after: "
        f"{updated_after}"
    )

    earthquakes_df = get_earthquakes(
        updated_after
    )

    earthquakes_df["_INGESTED_AT"] = (
        pd.Timestamp.now(tz="UTC")
    )

    print(
        f"Rows received from USGS: "
        f"{len(earthquakes_df)}"
    )

    if earthquakes_df.empty:

        print(
            "No new or updated earthquakes."
        )

    else:

        print(
            f"Unique IDs received: "
            f"{earthquakes_df['id'].nunique()}"
        )

        duplicate_count = (
            earthquakes_df["id"]
            .duplicated()
            .sum()
        )

        print(
            f"Duplicate IDs received: "
            f"{duplicate_count}"
        )

        if duplicate_count > 0:
            raise ValueError(
                f"USGS returned "
                f"{duplicate_count} duplicate IDs."
            )

        # -----------------------------------------------------------
        # Temporary table
        # -----------------------------------------------------------

        cursor = connection.cursor()

        cursor.execute("""
            CREATE OR REPLACE TEMPORARY TABLE
            USGS_EARTHQUAKES_INCREMENTAL
            LIKE BLUE_DOT_PLOT.RAW.USGS_EARTHQUAKES
        """)

        cursor.close()

        # -----------------------------------------------------------
        # Upload incremental data
        # -----------------------------------------------------------

        success, number_of_chunks, number_of_rows, output = (
            write_pandas(
                connection,
                earthquakes_df,
                "USGS_EARTHQUAKES_INCREMENTAL",
                database="BLUE_DOT_PLOT",
                schema="RAW",
                auto_create_table=False,
                quote_identifiers=False,
                use_logical_type=True,
            )
        )

        print(
            f"Temporary table upload successful: "
            f"{success}"
        )

        print(
            f"Rows uploaded to temporary table: "
            f"{number_of_rows}"
        )

        if not success:
            raise RuntimeError(
                "Incremental upload to temporary table "
                "was not successful."
            )

        # -----------------------------------------------------------
        # MERGE
        # -----------------------------------------------------------

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

                target.MMI = source.MMI,
                target.CDI = source.CDI,
                target.FELT = source.FELT,
                target.TSUNAMI = source.TSUNAMI,
                target.ALERT = source.ALERT,
                target.SIG = source.SIG,
                target.URL = source.URL,
                target.DETAIL = source.DETAIL,
                target.IDS = source.IDS,
                target.TYPES = source.TYPES,
                target.CODE = source.CODE,

                target._INGESTED_AT = source._INGESTED_AT

            WHEN NOT MATCHED THEN INSERT (
                ID,
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
                UPDATED,
                PLACE,
                TYPE,
                HORIZONTALERROR,
                DEPTHERROR,
                MAGERROR,
                MAGNST,
                STATUS,
                MMI,
                CDI,
                FELT,
                TSUNAMI,
                ALERT,
                SIG,
                URL,
                DETAIL,
                IDS,
                TYPES,
                CODE,
                _INGESTED_AT
            )

            VALUES (
                source.ID,
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
                source.UPDATED,
                source.PLACE,
                source.TYPE,
                source.HORIZONTALERROR,
                source.DEPTHERROR,
                source.MAGERROR,
                source.MAGNST,
                source.STATUS,
                source.MMI,
                source.CDI,
                source.FELT,
                source.TSUNAMI,
                source.ALERT,
                source.SIG,
                source.URL,
                source.DETAIL,
                source.IDS,
                source.TYPES,
                source.CODE,
                source._INGESTED_AT
            )
        """)

        print(
            "MERGE completed successfully."
        )

        cursor.close()

finally:

    connection.close()

    print(
        "Connection closed."
    )