with place_candidates as (

    select
        event_id,
        geoname_id,
        place_name,
        feature_code,
        country_code,
        population,
        distance_km,
        distance_miles,
        candidate_type

    from {{ ref('int_earthquake_place_candidates') }}

),

places as (

    select
        geoname_id,
        latitude as place_latitude,
        longitude as place_longitude

    from {{ ref('geonames_cities1000') }}

),

final as (

    select
        place_candidates.event_id,

        place_candidates.geoname_id,
        place_candidates.place_name,
        place_candidates.feature_code,
        place_candidates.country_code,
        place_candidates.population,

        places.place_latitude,
        places.place_longitude,

        place_candidates.distance_km,
        place_candidates.distance_miles,

        place_candidates.candidate_type,

        row_number() over (
            partition by place_candidates.event_id
            order by
                place_candidates.distance_km,
                place_candidates.geoname_id
        ) as place_rank

    from place_candidates

    left join places
        on place_candidates.geoname_id = places.geoname_id

)

select *
from final