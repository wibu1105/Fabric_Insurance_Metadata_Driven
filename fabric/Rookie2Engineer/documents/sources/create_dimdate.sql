CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    date_long_description VARCHAR(50),
    date_short_description VARCHAR(20),
    day_name VARCHAR(20),
    day_short_name VARCHAR(10),
    month_name VARCHAR(20),
    month_short_name VARCHAR(10),
    day_of_year INT,
    week_number INT,
    day_of_week INT,
    month_number INT,
    day_of_month INT,
    quarter_number INT,
    day_of_quarter INT,
    year_number INT,
    is_weekend BIT
);

INSERT INTO dim_date (
    date_key,
    full_date,
    date_long_description,
    date_short_description,
    day_name,
    day_short_name,
    month_name,
    month_short_name,
    day_of_year,
    week_number,
    day_of_week,
    month_number,
    day_of_month,
    quarter_number,
    day_of_quarter,
    year_number,
    is_weekend
)
SELECT
    CAST(FORMAT(full_date, 'yyyyMMdd') AS INT) AS date_key,
    full_date,
    DATENAME(WEEKDAY, full_date) + ', ' + DATENAME(MONTH, full_date) + ' ' + CAST(DAY(full_date) AS VARCHAR) + ', ' + CAST(YEAR(full_date) AS VARCHAR) AS date_long_description,
    LEFT(DATENAME(MONTH, full_date), 3) + ' ' + CAST(DAY(full_date) AS VARCHAR) + ', ' + CAST(YEAR(full_date) AS VARCHAR) AS date_short_description,
    DATENAME(WEEKDAY, full_date) AS day_name,
    LEFT(DATENAME(WEEKDAY, full_date), 3) AS day_short_name,
    DATENAME(MONTH, full_date) AS month_name,
    LEFT(DATENAME(MONTH, full_date), 3) AS month_short_name,
    DATEPART(DAYOFYEAR, full_date) AS day_of_year,
    DATEPART(WEEK, full_date) AS week_number,
    DATEPART(WEEKDAY, full_date) AS day_of_week,
    MONTH(full_date) AS month_number,
    DAY(full_date) AS day_of_month,
    DATEPART(QUARTER, full_date) AS quarter_number,
    DATEDIFF(DAY, DATEADD(QUARTER, DATEDIFF(QUARTER, 0, full_date), 0), full_date) + 1 AS day_of_quarter,
    YEAR(full_date) AS year_number,
    CASE 
        WHEN DATENAME(WEEKDAY, full_date) IN ('Saturday', 'Sunday') THEN 1 
        ELSE 0 
    END AS is_weekend
FROM (
    SELECT 
        DATEADD(
            DAY,
            ones.n 
            + tens.n * 10 
            + hundreds.n * 100 
            + thousands.n * 1000 
            + ten_thousands.n * 10000, 
            '2000-01-01'
        ) AS full_date
    FROM (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) ones(n)
    CROSS JOIN (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) tens(n)
    CROSS JOIN (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) hundreds(n)
    CROSS JOIN (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) thousands(n)
    CROSS JOIN (VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9)) ten_thousands(n)
) d
WHERE full_date <= '2099-12-31';

SELECT count(*) as insert_count
FROM dim_date;