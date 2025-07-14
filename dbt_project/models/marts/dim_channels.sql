SELECT DISTINCT
    channel_name
FROM {{ ref('stg_telegram_messages') }}
WHERE channel_name IS NOT NULL