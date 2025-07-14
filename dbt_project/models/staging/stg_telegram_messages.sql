WITH source AS (
    SELECT
        data,
        loaded_at
    FROM {{ source('raw_telegram', 'telegram_messages') }}
)

SELECT
    (data ->> 'message_id')::BIGINT AS message_id,
    (data ->> 'channel_name')::TEXT AS channel_name,
    (data ->> 'text')::TEXT AS message_text,
    (data ->> 'date')::TIMESTAMP AS message_date,
    (data ->> 'views')::INT AS view_count,
    (data ->> 'has_image')::BOOLEAN AS has_image,
    loaded_at
FROM source
WHERE (data ->> 'message_id') IS NOT NULL