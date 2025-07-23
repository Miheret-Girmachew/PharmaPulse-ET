-- A test fails if this query returns any rows
select
    message_id,
    view_count
from {{ ref('fct_messages') }}
where view_count < 0    