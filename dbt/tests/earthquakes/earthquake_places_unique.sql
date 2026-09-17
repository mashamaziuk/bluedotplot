select
    event_id,
    geoname_id,
    count(*) as row_count

from {{ ref('earthquake_places') }}

group by
    event_id,
    geoname_id

having count(*) > 1