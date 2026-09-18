select
    sequence_id,
    event_id,
    loaded_at_utc
from {{ source('usgs', 'usgs_earthquake_sequence_members') }}