with earthquakes as (

    select
        event_id,
        magnitude,
        latitude,
        longitude,

        case
            when magnitude < 4 then 50
            when magnitude < 5 then 100
            when magnitude < 6 then 200
            when magnitude < 7 then 300
            when magnitude < 8 then 400
            else 750
        end as candidate_search_radius_km

    from {{ ref('int_earthquakes_base') }}

    where event_time_utc >= dateadd(day, -14, current_timestamp())

),

populated_places as (

    select
        geoname_id,
        place_name,
        latitude,
        longitude,
        feature_code,
        country_code,
        nullif(population, 0) as population

    from {{ ref('geonames_cities1000') }}

),

earthquake_points as (

    select
        event_id,
        magnitude,
        candidate_search_radius_km,
        st_makepoint(longitude, latitude) as earthquake_point

    from earthquakes

),

place_points as (

    select
        geoname_id,
        place_name,
        feature_code,
        country_code,
        population,
        st_makepoint(longitude, latitude) as place_point

    from populated_places

),

candidate_places as (

    select
        earthquake_points.event_id,
        earthquake_points.magnitude,
        earthquake_points.candidate_search_radius_km,

        place_points.geoname_id,
        place_points.place_name,
        place_points.feature_code,
        place_points.country_code,
        place_points.population,

        st_distance(
            earthquake_points.earthquake_point,
            place_points.place_point
        ) as distance_meters

    from earthquake_points

    inner join place_points
        on st_dwithin(
            earthquake_points.earthquake_point,
            place_points.place_point,
            earthquake_points.candidate_search_radius_km * 1000
        )

),

final as (

    select
        event_id,
        magnitude,
        candidate_search_radius_km,

        geoname_id,
        place_name,
        feature_code,
        country_code,
        population,

        distance_meters / 1000 as distance_km,
        distance_meters / 1609.344 as distance_miles

    from candidate_places

)

select *
from final