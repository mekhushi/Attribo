
WITH ordered_touchpoints AS (
    SELECT 
        user_id,
        channel,
        timestamp,
        converted,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp ASC) as touchpoint_rank
    FROM user_journeys
),
user_conversion_status AS (
    SELECT 
        user_id,
        MAX(converted) as is_converted
    FROM user_journeys
    GROUP BY user_id
)
SELECT 
    ot.user_id,
    STRING_AGG(ot.channel, ' > ' ORDER BY ot.timestamp ASC) as path,
    ucs.is_converted
FROM ordered_touchpoints ot
JOIN user_conversion_status ucs ON ot.user_id = ucs.user_id
GROUP BY ot.user_id, ucs.is_converted;

WITH converted_users AS (
    SELECT DISTINCT user_id 
    FROM user_journeys
    WHERE converted = 1
),
touchpoints_with_rank AS (
    SELECT 
        user_id,
        channel,
        timestamp,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp ASC) as first_touch_rank,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as last_touch_rank
    FROM user_journeys
    WHERE user_id IN (SELECT user_id FROM converted_users)
),
first_touch_attribution AS (
    SELECT 
        channel,
        COUNT(*) as first_touch_conversions
    FROM touchpoints_with_rank
    WHERE first_touch_rank = 1
    GROUP BY channel
),
last_touch_attribution AS (
    SELECT 
        channel,
        COUNT(*) as last_touch_conversions
    FROM touchpoints_with_rank
    WHERE last_touch_rank = 1
    GROUP BY channel
)
SELECT 
    coalesce(ft.channel, lt.channel) as channel,
    coalesce(ft.first_touch_conversions, 0) as sql_first_touch,
    coalesce(lt.last_touch_conversions, 0) as sql_last_touch
FROM first_touch_attribution ft
FULL OUTER JOIN last_touch_attribution lt ON ft.channel = lt.channel
ORDER BY sql_last_touch DESC;

WITH raw_transitions AS (
    SELECT 
        user_id,
        channel as state_from,
        LEAD(channel) OVER (PARTITION BY user_id ORDER BY timestamp ASC) as state_to,
        converted,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) as last_touch_rank
    FROM user_journeys
),
all_transitions AS (
    SELECT 
        state_from,
        state_to
    FROM raw_transitions
    WHERE state_to IS NOT NULL
    
    UNION ALL
    
    SELECT 
        '(Start)' as state_from,
        channel as state_to
    FROM user_journeys
    WHERE (user_id, timestamp) IN (
        SELECT user_id, MIN(timestamp) FROM user_journeys GROUP BY user_id
    )
    
    UNION ALL
    
    SELECT 
        state_from,
        '(Conversion)' as state_to
    FROM raw_transitions
    WHERE last_touch_rank = 1 AND converted = 1
    
    UNION ALL
    
    SELECT 
        state_from,
        '(Null)' as state_to
    FROM raw_transitions
    WHERE last_touch_rank = 1 AND converted = 0
)
SELECT 
    state_from,
    state_to,
    COUNT(*) as transition_count
FROM all_transitions
GROUP BY state_from, state_to
ORDER BY state_from, transition_count DESC;
