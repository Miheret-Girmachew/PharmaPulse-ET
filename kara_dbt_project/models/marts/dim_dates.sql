select
    date_day::date as date_key,
    extract(year from date_day) as year,
    extract(month from date_day) as month,
    extract(day from date_day) as day,
    extract(dow from date_day) as day_of_week 
from generate_series(
    '2022-01-01'::date,
    current_date + interval '1 year',
    '1 day'::interval
) as date_day