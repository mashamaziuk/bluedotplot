{{ config(
    materialized='incremental',
    incremental_strategy='delete+insert',
    unique_key='event_id'
) }}

with earthquakes as (

    select
        event_id,
        event_time_utc,
        updated_at_utc,
        magnitude,
        st_makepoint(longitude, latitude) as earthquake_point,

        case
            when magnitude < 4 then 100
            when magnitude < 5 then 200
            when magnitude < 6 then 400
            when magnitude < 7 then 700
            when magnitude < 8 then 1000
            else 1500
        end as candidate_search_radius_km

    from {{ ref('int_earthquakes_base') }}

    where event_time_utc >= dateadd(day, -30, current_timestamp())

    {% if is_incremental() %}

        and updated_at_utc >= (
            select coalesce(
                dateadd(hour, -1, max(updated_at_utc)),
                '1900-01-01'::timestamp_ntz
            )
            from {{ this }}
        )

    {% endif %}

),

populated_places as (

    select
        geoname_id,
        place_name,
        latitude,
        longitude,
        feature_code,
        country_code,
        nullif(population, 0) as population,
        st_makepoint(longitude, latitude) as place_point

    from {{ ref('geonames_cities1000') }}

    where population >= 1000

),

nearest_populated_place as (

    select
        earthquakes.event_id,
        earthquakes.event_time_utc,
        earthquakes.updated_at_utc,
        earthquakes.magnitude,
        earthquakes.candidate_search_radius_km,

        populated_places.geoname_id,
        populated_places.place_name,
        populated_places.feature_code,
        populated_places.country_code,
        populated_places.population,

        st_distance(
            earthquakes.earthquake_point,
            populated_places.place_point
        ) as distance_meters,

        'nearest_populated_place' as candidate_type

    from earthquakes

    inner join populated_places
        on st_dwithin(
            earthquakes.earthquake_point,
            populated_places.place_point,
            earthquakes.candidate_search_radius_km * 1000
        )

    qualify row_number() over (
        partition by earthquakes.event_id
        order by distance_meters
    ) = 1

),

nearest_large_places as (

    select
        earthquakes.event_id,
        earthquakes.event_time_utc,
        earthquakes.updated_at_utc,
        earthquakes.magnitude,
        earthquakes.candidate_search_radius_km,

        populated_places.geoname_id,
        populated_places.place_name,
        populated_places.feature_code,
        populated_places.country_code,
        populated_places.population,

        st_distance(
            earthquakes.earthquake_point,
            populated_places.place_point
        ) as distance_meters,

        'large_populated_place' as candidate_type

    from earthquakes

    inner join populated_places
        on populated_places.population >= 10000
        and st_dwithin(
            earthquakes.earthquake_point,
            populated_places.place_point,
            earthquakes.candidate_search_radius_km * 1000
        )

    where not exists (
        select 1
        from nearest_populated_place
        where nearest_populated_place.event_id = earthquakes.event_id
          and nearest_populated_place.geoname_id = populated_places.geoname_id
    )

    qualify row_number() over (
        partition by earthquakes.event_id
        order by distance_meters
    ) <= 3

),

capital_places as (

    select
        geoname_id,
        place_name,
        latitude,
        longitude,
        feature_code,
        country_code,
        nullif(population, 0) as population,
        st_makepoint(longitude, latitude) as place_point

    from {{ ref('geonames_cities1000') }}

    where feature_code in ('PPLC', 'PPLA')

),

nearest_capital as (

    select
        earthquakes.event_id,
        earthquakes.event_time_utc,
        earthquakes.updated_at_utc,
        earthquakes.magnitude,
        earthquakes.candidate_search_radius_km,

        capital_places.geoname_id,
        capital_places.place_name,
        capital_places.feature_code,
        capital_places.country_code,
        capital_places.population,

        st_distance(
            earthquakes.earthquake_point,
            capital_places.place_point
        ) as distance_meters,

        'capital_city' as candidate_type

    from earthquakes

    inner join capital_places
        on st_dwithin(
            earthquakes.earthquake_point,
            capital_places.place_point,
            earthquakes.candidate_search_radius_km * 1000
        )

    where not exists (
        select 1
        from nearest_populated_place
        where nearest_populated_place.event_id = earthquakes.event_id
          and nearest_populated_place.geoname_id = capital_places.geoname_id
    )
      and not exists (
        select 1
        from nearest_large_places
        where nearest_large_places.event_id = earthquakes.event_id
          and nearest_large_places.geoname_id = capital_places.geoname_id
    )

    qualify row_number() over (
        partition by earthquakes.event_id
        order by distance_meters
    ) = 1

),

candidates as (

    select *
    from nearest_populated_place

    union all

    select *
    from nearest_large_places

    union all

    select *
    from nearest_capital

)

select
    event_id,
    event_time_utc,
    updated_at_utc,
    magnitude,
    candidate_search_radius_km,

    geoname_id,
    place_name,
    feature_code,
    country_code,
    population,

    distance_meters / 1000 as distance_km,
    distance_meters / 1609.344 as distance_miles,

    candidate_type

from candidates