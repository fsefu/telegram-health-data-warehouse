WITH raw_data AS (
    SELECT *
    FROM {{ ref('cleaned_data') }}
)
SELECT 
    id, 
    created_at,
    product_name,
    quantity
FROM raw_data;
