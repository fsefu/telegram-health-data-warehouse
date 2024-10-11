-- models/marts/final_transformed_table.sql
WITH transformed_data AS (
    SELECT
        id,
        product_name,
        SUM(quantity) AS total_quantity
    FROM {{ ref('stg_raw_data') }}
    GROUP BY id, product_name
)
SELECT * FROM transformed_data;
