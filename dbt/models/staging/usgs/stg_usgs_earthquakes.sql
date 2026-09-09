select
    id as event_id,
    time as event_time_utc,
    updated as updated_at_utc,

    latitude,
    longitude,
    depth as depth_km,

    mag as magnitude,
    magtype as magnitude_type,

    nst as location_station_count,
    gap as azimuthal_gap_deg,
    dmin as nearest_station_distance_deg,
    rms as rms_residual_sec,

    net as preferred_network,
    place,
    type as event_type,

    horizontalerror as horizontal_location_error_km,
    deptherror as depth_error_km,
    magerror as magnitude_error,
    magnst as magnitude_station_count,

    status as event_status,

    -- Earthquake impact / intensity
    mmi,
    cdi,
    felt as felt_count,

    -- Tsunami and significance
    tsunami as tsunami_flag,
    alert,
    sig as significance_score,

    -- USGS event metadata
    url,
    detail,
    ids,
    types,
    code

from {{ source('usgs', 'usgs_earthquakes') }}