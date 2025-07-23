with source as (
    select * from {{ source('raw_telegram', 'telegram_messages') }}
)

select
    -- Extract fields from the JSONB column
    (data ->> 'id')::bigint as message_id,
    (data ->> 'date')::timestamp with time zone as message_date,
    (data ->> 'text') as message_text,
    (data ->> 'sender_id')::bigint as sender_id,
    (data ->> 'channel') as channel_name,
    (data ->> 'views')::integer as view_count,
    (data ->> 'has_photo')::boolean as has_photo,
    loaded_at
from source