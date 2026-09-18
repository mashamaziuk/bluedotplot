import os
import time
from datetime import datetime, timedelta, timezone

import requests
import snowflake.connector
from dotenv import load_dotenv


load_dotenv()


USGS_EVENT_URL = (
    "https://earthquake.usgs.gov/fdsnws/event/1/query"
)

DATABASE = "BLUE_DOT_PLOT"
SCHEMA = "RAW"

SEQUENCES_TABLE = (
    f"{DATABASE}.{SCHEMA}.USGS_EARTHQUAKE_SEQUENCES"
)

MEMBERS_TABLE = (
    f"{DATABASE}.{SCHEMA}.USGS_EARTHQUAKE_SEQUENCE_MEMBERS"
)

LOOKBACK_HOURS = 2

MAX_RETRIES = 5
REQUEST_TIMEOUT = 60


def request_json(session, params):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(
                USGS_EVENT_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:
            if attempt == MAX_RETRIES:
                raise

            print(
                f"Request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): "
                f"{error}"
            )

            time.sleep(2 ** (attempt - 1))

    raise RuntimeError("USGS request failed")


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=DATABASE,
        schema=SCHEMA,
    )


def get_recent_discovery_events(session):
    end_time = datetime.now(timezone.utc)

    start_time = end_time - timedelta(
        hours=LOOKBACK_HOURS
    )

    data = request_json(
        session,
        {
            "format": "geojson",
            "starttime": start_time.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "endtime": end_time.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "producttype": "event-sequence",
            "limit": 20000,
            "orderby": "time-asc",
        },
    )

    return data["features"]


def get_event(session, event_id):
    return request_json(
        session,
        {
            "format": "geojson",
            "eventid": event_id,
        },
    )


def get_sequence_product(event):
    products = (
        event.get("properties", {})
        .get("products", {})
        .get("event-sequence", [])
    )

    if not products:
        return None

    return max(
        products,
        key=lambda product: product.get(
            "updateTime",
            0,
        ),
    )


def get_sequence_definition(product):
    product_id = product.get("id", "")
    parts = product_id.split(":")

    if len(parts) < 6:
        return None

    sequence_id = parts[-2]

    properties = product.get("properties", {})

    event_source = properties.get("eventsource")
    event_source_code = properties.get(
        "eventsourcecode"
    )

    if not event_source or not event_source_code:
        return None

    return {
        "sequence_id": sequence_id,
        "mainshock_event_id": (
            f"{event_source}{event_source_code}"
        ),
        "sequence_type": properties.get(
            "sequence-type"
        ),
        "center_latitude": float(
            properties["circle-latitude"]
        ),
        "center_longitude": float(
            properties["circle-longitude"]
        ),
        "radius_km": float(
            properties["circle-radiuskm"]
        ),
        "start_time": properties["starttime"],
        "end_time": properties["endtime"],
        "generated_by": properties.get(
            "generated-by"
        ),
        "product_update_time": datetime.fromtimestamp(
            product["updateTime"] / 1000,
            tz=timezone.utc,
        ),
    }


def get_sequence_members(session, sequence):
    data = request_json(
        session,
        {
            "format": "geojson",
            "latitude": sequence["center_latitude"],
            "longitude": sequence["center_longitude"],
            "maxradiuskm": sequence["radius_km"],
            "starttime": sequence["start_time"],
            "endtime": sequence["end_time"],
            "eventtype": "earthquake",
            "limit": 20000,
            "orderby": "time-asc",
        },
    )

    return [
        feature["id"]
        for feature in data["features"]
        if feature.get("id")
    ]


def replace_sequence(
    connection,
    sequence,
    member_event_ids,
):
    cursor = connection.cursor()

    try:
        cursor.execute(
            f"""
            DELETE FROM {MEMBERS_TABLE}
            WHERE sequence_id = %s
            """,
            (sequence["sequence_id"],),
        )

        cursor.execute(
            f"""
            DELETE FROM {SEQUENCES_TABLE}
            WHERE sequence_id = %s
            """,
            (sequence["sequence_id"],),
        )

        cursor.execute(
            f"""
            INSERT INTO {SEQUENCES_TABLE} (
                sequence_id,
                mainshock_event_id,
                sequence_type,
                center_latitude,
                center_longitude,
                radius_km,
                start_time_utc,
                end_time_utc,
                generated_by,
                product_update_time
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                sequence["sequence_id"],
                sequence["mainshock_event_id"],
                sequence["sequence_type"],
                sequence["center_latitude"],
                sequence["center_longitude"],
                sequence["radius_km"],
                sequence["start_time"],
                sequence["end_time"],
                sequence["generated_by"],
                sequence["product_update_time"],
            ),
        )

        cursor.executemany(
            f"""
            INSERT INTO {MEMBERS_TABLE} (
                sequence_id,
                event_id
            )
            VALUES (%s, %s)
            """,
            [
                (
                    sequence["sequence_id"],
                    event_id,
                )
                for event_id in member_event_ids
            ],
        )

    finally:
        cursor.close()


def main():
    session = requests.Session()

    print("=" * 60)
    print("USGS SEQUENCE INCREMENTAL LOAD")
    print("=" * 60)

    connection = None

    try:
        discovery_events = get_recent_discovery_events(
            session
        )

        print(
            "Recent events with event-sequence product: "
            f"{len(discovery_events)}"
        )

        sequences = {}

        for discovery_event in discovery_events:
            event_id = discovery_event["id"]

            event = get_event(
                session,
                event_id,
            )

            product = get_sequence_product(event)

            if product is None:
                continue

            sequence = get_sequence_definition(
                product
            )

            if sequence is None:
                continue

            sequences[
                sequence["sequence_id"]
            ] = sequence

        print(
            "Unique sequences found: "
            f"{len(sequences)}"
        )

        connection = get_connection()

        loaded_members = 0

        for sequence_id, sequence in sequences.items():
            member_event_ids = get_sequence_members(
                session,
                sequence,
            )

            replace_sequence(
                connection,
                sequence,
                member_event_ids,
            )

            connection.commit()

            loaded_members += len(
                member_event_ids
            )

            print(
                f"{sequence_id} | "
                f"members={len(member_event_ids)}"
            )

        print()
        print("=" * 60)
        print("INCREMENTAL LOAD COMPLETED")
        print("=" * 60)
        print(
            f"Sequences updated: {len(sequences)}"
        )
        print(
            f"Memberships loaded: {loaded_members}"
        )

    except Exception:
        if connection is not None:
            connection.rollback()

        raise

    finally:
        if connection is not None:
            connection.close()

        session.close()


if __name__ == "__main__":
    main()