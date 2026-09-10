with earthquakes as (

    select *
    from {{ ref('stg_usgs_earthquakes') }}

),

magnitude_types as (

    select
        magnitude_type,
        magnitude_family,
        magnitude_name,
        magnitude_description,
        magnitude_measurement_basis

    from {{ ref('earthquake_magnitude_types') }}

),

base as (

    select
        earthquakes.event_id,

        -- Time
        to_timestamp_ntz(earthquakes.event_time_utc / 1000) as event_time_utc,
        to_timestamp_ntz(earthquakes.updated_at_utc / 1000) as updated_at_utc,

        -- Location
        earthquakes.latitude,
        earthquakes.longitude,
        earthquakes.depth_km,
        earthquakes.depth_km * 0.621371 as depth_miles,

        -- Magnitude
        earthquakes.magnitude,
        earthquakes.magnitude_type,
        magnitude_types.magnitude_family,
        magnitude_types.magnitude_name,
        magnitude_types.magnitude_description,
        magnitude_types.magnitude_measurement_basis,

        -- Event information
        earthquakes.event_type,
        earthquakes.event_status,
        earthquakes.place,
        earthquakes.preferred_network,

        -- Location quality
        earthquakes.location_station_count,
        earthquakes.azimuthal_gap_deg,
        earthquakes.nearest_station_distance_deg,
        earthquakes.rms_residual_sec,
        earthquakes.horizontal_location_error_km,
        earthquakes.depth_error_km,
        earthquakes.depth_error_km * 0.621371 as depth_error_miles,

        -- Magnitude quality
        earthquakes.magnitude_error,
        earthquakes.magnitude_station_count,

        -- Impact
        earthquakes.mmi,
        earthquakes.cdi,
        earthquakes.felt_count,
        earthquakes.tsunami_flag,
        earthquakes.alert,
        earthquakes.significance_score,

        -- USGS metadata
        earthquakes.url,
        earthquakes.detail,
        earthquakes.ids,
        earthquakes.types,
        earthquakes.code

    from earthquakes

    left join magnitude_types
    on earthquakes.magnitude_type = magnitude_types.magnitude_type

)

select *
from base
