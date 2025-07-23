with message_source as (
    select distinct channel_name
    from {{ ref('stg_telegram_messages') }}
    where channel_name is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
    channel_name
from message_source