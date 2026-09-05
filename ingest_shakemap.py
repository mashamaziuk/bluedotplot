import os
import time
from datetime import datetime, timedelta, timezone

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from snowflake.connector.pandas_tools import write_pandas


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DAYS_BACK = 7
MIN_MAGNITUDE = 3.0

EVENT_API_URL = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query"
)

DETAIL_URL_TEMPLATE = (
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/"
    "detail/{}.geojson"
)

SHAKEMAP_PRODUCT_KEY = (
    "download/coverage_mmi_medium_res.covjson"
)


# --------------------------------------------------
# HTTP session with retries
# --------------------------------------------------

session = requests.Session()

retry_strategy = Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)

adapter = HTTPAdapter(
    max_retries=retry_strategy
)

session.mount("https://", adapter)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
)


try:

    # --------------------------------------------------
    # 1. Define time window
    # --------------------------------------------------

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=DAYS_BACK)

    print("Requesting earthquakes:")
    print("From:", start_time.isoformat())
    print("To:", end_time.isoformat())
    print("Minimum magnitude:", MIN_MAGNITUDE)


    # --------------------------------------------------
    # 2. Get earthquake list
    # --------------------------------------------------

    params = {
        "format": "geojson",
        "starttime": start_time.isoformat(),
        "endtime": end_time.isoformat(),
        "minmagnitude": MIN_MAGNITUDE,
        "limit": 20000,
        "orderby": "time-asc",
    }

    response = session.get(
        EVENT_API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    earthquake_data = response.json()

    features = earthquake_data.get("features", [])

    print("\nEarthquakes received:", len(features))


    # --------------------------------------------------
    # 3. Process events
    # --------------------------------------------------

    all_rows = []

    events_with_shakemap = 0
    events_without_shakemap = 0
    failed_events = 0

    for i, feature in enumerate(features, start=1):

        event_id = feature["id"]

        detail_url = DETAIL_URL_TEMPLATE.format(event_id)

        # --------------------------------------------------
        # Get event details
        # --------------------------------------------------

        try:

            detail_response = session.get(
                detail_url,
                timeout=60,
            )

            detail_response.raise_for_status()

            detail_data = detail_response.json()

        except Exception as e:

            print(
                f"{i}/{len(features)} "
                f"{event_id}: "
                f"failed to get details: {e}"
            )

            failed_events += 1

            continue


        # --------------------------------------------------
        # Find ShakeMap
        # --------------------------------------------------

        properties = detail_data.get(
            "properties",
            {}
        )

        products = properties.get(
            "products",
            {}
        )

        shakemap_products = products.get(
            "shakemap",
            []
        )

        if not shakemap_products:

            events_without_shakemap += 1

            print(
                f"{i}/{len(features)} "
                f"{event_id}: no ShakeMap"
            )

            continue


        # --------------------------------------------------
        # Select preferred ShakeMap
        # --------------------------------------------------

        shakemap = max(
            shakemap_products,
            key=lambda p: p.get(
                "preferredWeight",
                0
            ),
        )


        # --------------------------------------------------
        # Find medium-resolution MMI
        # --------------------------------------------------

        contents = shakemap.get(
            "contents",
            {}
        )

        if SHAKEMAP_PRODUCT_KEY not in contents:

            events_without_shakemap += 1

            print(
                f"{i}/{len(features)} "
                f"{event_id}: "
                f"medium MMI not available"
            )

            continue


        mmi_url = contents[
            SHAKEMAP_PRODUCT_KEY
        ]["url"]


        # --------------------------------------------------
        # Download MMI grid
        # --------------------------------------------------

        try:

            mmi_response = session.get(
                mmi_url,
                timeout=60,
            )

            mmi_response.raise_for_status()

            mmi_data = mmi_response.json()

        except Exception as e:

            print(
                f"{i}/{len(features)} "
                f"{event_id}: "
                f"failed to download MMI: {e}"
            )

            failed_events += 1

            continue


        # --------------------------------------------------
        # Get grid dimensions
        # --------------------------------------------------

        axes = mmi_data["domain"]["axes"]

        x_axis = axes["x"]
        y_axis = axes["y"]

        x_start = x_axis["start"]
        x_stop = x_axis["stop"]
        x_num = x_axis["num"]

        y_start = y_axis["start"]
        y_stop = y_axis["stop"]
        y_num = y_axis["num"]


        # --------------------------------------------------
        # Build coordinates
        # --------------------------------------------------

        if x_num > 1:

            longitudes = [
                x_start
                + i * (x_stop - x_start)
                / (x_num - 1)
                for i in range(x_num)
            ]

        else:

            longitudes = [x_start]


        if y_num > 1:

            latitudes = [
                y_start
                + i * (y_stop - y_start)
                / (y_num - 1)
                for i in range(y_num)
            ]

        else:

            latitudes = [y_start]


        # --------------------------------------------------
        # Get MMI values
        # --------------------------------------------------

        mmi_values = mmi_data[
            "ranges"
        ]["MMI"]["values"]

        expected_points = x_num * y_num

        if len(mmi_values) != expected_points:

            print(
                f"{i}/{len(features)} "
                f"{event_id}: "
                f"unexpected number of points "
                f"(expected {expected_points}, "
                f"got {len(mmi_values)})"
            )

            failed_events += 1

            continue


        # --------------------------------------------------
        # Convert grid into rows
        # --------------------------------------------------

        for row_index, latitude in enumerate(
            latitudes
        ):

            start = row_index * x_num
            end = start + x_num

            row_mmi = mmi_values[
                start:end
            ]

            for longitude, mmi in zip(
                longitudes,
                row_mmi
            ):

                all_rows.append(
                    {
                        "EVENT_ID": event_id,
                        "LATITUDE": latitude,
                        "LONGITUDE": longitude,
                        "MMI": mmi,
                    }
                )


        events_with_shakemap += 1

        print(
            f"{i}/{len(features)} "
            f"{event_id}: "
            f"{expected_points:,} points"
        )

        # Small pause between requests
        time.sleep(0.1)


    # --------------------------------------------------
    # 4. Create DataFrame
    # --------------------------------------------------

    df = pd.DataFrame(
        all_rows,
        columns=[
            "EVENT_ID",
            "LATITUDE",
            "LONGITUDE",
            "MMI",
        ],
    )

    print("\n--------------------------------")
    print("Ingestion summary")
    print("--------------------------------")

    print(
        "Events received:",
        len(features),
    )

    print(
        "Events with ShakeMap:",
        events_with_shakemap,
    )

    print(
        "Events without ShakeMap:",
        events_without_shakemap,
    )

    print(
        "Failed events:",
        failed_events,
    )

    print(
        "Total grid rows:",
        f"{len(df):,}",
    )


    if df.empty:

        print(
            "\nNo ShakeMap data to load."
        )

        exit()


    # --------------------------------------------------
    # 5. Clean data
    # --------------------------------------------------

    df["LATITUDE"] = pd.to_numeric(
        df["LATITUDE"],
        errors="coerce",
    )

    df["LONGITUDE"] = pd.to_numeric(
        df["LONGITUDE"],
        errors="coerce",
    )

    df["MMI"] = pd.to_numeric(
        df["MMI"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "EVENT_ID",
            "LATITUDE",
            "LONGITUDE",
            "MMI",
        ]
    )

    print(
        "Rows after cleaning:",
        f"{len(df):,}",
    )


    # --------------------------------------------------
    # 6. Create temporary table
    # --------------------------------------------------

    cursor = conn.cursor()

    cursor.execute("""
        CREATE OR REPLACE TEMPORARY TABLE
        TEMP_USGS_SHAKEMAP (
            EVENT_ID VARCHAR,
            LATITUDE FLOAT,
            LONGITUDE FLOAT,
            MMI FLOAT
        )
    """)


    # --------------------------------------------------
    # 7. Upload to Snowflake
    # --------------------------------------------------

    success, nchunks, nrows, _ = write_pandas(
        conn,
        df,
        "TEMP_USGS_SHAKEMAP",
        auto_create_table=False,
        overwrite=False,
    )

    print("\nTemporary table upload:")
    print("Success:", success)
    print("Rows uploaded:", nrows)


    if not success:

        raise RuntimeError(
            "Failed to upload data to Snowflake"
        )


    # --------------------------------------------------
    # 8. Merge into RAW table
    # --------------------------------------------------

    cursor.execute("""
        MERGE INTO RAW.USGS_SHAKEMAP AS target
        USING TEMP_USGS_SHAKEMAP AS source

        ON target.EVENT_ID = source.EVENT_ID
        AND target.LATITUDE = source.LATITUDE
        AND target.LONGITUDE = source.LONGITUDE

        WHEN MATCHED THEN UPDATE SET
            target.MMI = source.MMI

        WHEN NOT MATCHED THEN INSERT (
            EVENT_ID,
            LATITUDE,
            LONGITUDE,
            MMI
        )
        VALUES (
            source.EVENT_ID,
            source.LATITUDE,
            source.LONGITUDE,
            source.MMI
        )
    """)

    print(
        "\nMERGE completed successfully."
    )


finally:

    conn.close()

    print("Connection closed.")