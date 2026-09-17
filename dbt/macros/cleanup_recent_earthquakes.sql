{% macro cleanup_recent_earthquakes() %}

    {% set candidates_relation = ref('int_earthquake_place_candidates') %}
    {% set places_relation = ref('earthquake_places') %}

    delete from {{ candidates_relation }}
    where event_time_utc < dateadd(day, -30, current_timestamp());

    delete from {{ places_relation }}
    where event_id not in (
        select event_id
        from {{ candidates_relation }}
    );

{% endmacro %}