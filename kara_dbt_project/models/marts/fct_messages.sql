with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    select * from {{ ref('dim_channels') }}
)

select
    -- Surrogate Keys
    {{ dbt_utils.generate_surrogate_key(['messages.message_id', 'messages.channel_name']) }} as message_key,
    channels.channel_key,
    messages.message_date::date as date_key,

    -- Degenerate Dimensions & Facts
    messages.message_id,
    messages.message_text,
    length(messages.message_text) as message_length,
    messages.has_photo,
    messages.view_count,
    messages.message_date

from messages
left join channels on messages.channel_name = channels.channel_name