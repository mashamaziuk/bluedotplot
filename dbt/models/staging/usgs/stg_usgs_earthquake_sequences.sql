select
    sequence_id,
    mainshock_event_id,
    sequence_type,
    center_latitude,
    center_longitude,
    radius_km,
    start_time_utc,
    end_time_utc,
    generated_by,
    product_update_time,
    loaded_at_utc
from {{ source('usgs', 'usgs_earthquake_sequences') }}