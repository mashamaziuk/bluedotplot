with earthquake_impacts as (

    select
        event_id,
        mmi,
        cdi,
        felt_count,
        tsunami_flag,
        alert,
        significance_score

    from {{ ref('stg_usgs_earthquakes') }}

)

select *
from earthquake_impacts