SELECT
    d.date AS full_date,
    EXTRACT(YEAR FROM d.date) AS year,
    EXTRACT(MONTH FROM d.date) AS month,
    EXTRACT(DAY FROM d.date) AS day,
    EXTRACT(DOW FROM d.date) AS day_of_week,
    TO_CHAR(d.date, 'Day') AS day_name,
    TO_CHAR(d.date, 'Month') AS month_name
FROM (
    SELECT DISTINCT(message_date::DATE) AS date
    FROM {{ ref('stg_telegram_messages') }}
) d