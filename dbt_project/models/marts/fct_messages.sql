SELECT
    message_id,
    channel_name,
    message_date::DATE AS date_key,
    message_text,
    view_count,
    has_image,
    LENGTH(message_text) as message_length
FROM {{ ref('stg_telegram_messages') }}