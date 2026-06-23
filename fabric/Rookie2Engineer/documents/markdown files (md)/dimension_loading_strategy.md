# Dimension Loading Strategy

## 1. SCD Type 1

### Overview

SCD Type 1 overwrites existing records when changes are detected. Historical values are not retained.

### Processing Logic

```python
# source_df: transformed source data

cols_to_minus = [c for c in source_df.columns]

diff_df = (
    source_df.select(cols_to_minus)
    .subtract(target_df.select(cols_to_minus))
)

diff_df.createOrReplaceTempView("diff_df")

spark.sql("""
MERGE INTO gold.DimVehicle AS tgt
USING diff_df AS src
ON tgt.vehicle_id = src.vehicle_id

WHEN MATCHED THEN
    UPDATE SET
        tgt.plate_number = src.plate_number,
        tgt.vehicle_brand = src.vehicle_brand
        -- Additional columns

WHEN NOT MATCHED THEN
    INSERT (
        vehicle_key,
        vehicle_id,
        customer_key,
        plate_number
        -- Additional columns
    )
    VALUES (
        src.vehicle_key,
        src.vehicle_id,
        src.customer_key,
        src.plate_number
        -- Additional columns
    )

WHEN NOT MATCHED BY SOURCE THEN
    UPDATE SET
        tgt.isDeleted = TRUE
""")
```

### Notes

- Existing records are updated directly.
- New records are inserted.
- Records no longer found in the source are soft deleted by setting `isDeleted = TRUE`.
- Historical changes are not preserved.

---

## 2. SCD Type 2 - Hydric

### Overview

SCD Type 2 preserves historical changes by expiring existing records and creating new versions.

### Change Detection Columns

- Bước 1: Xác định các record thay đổi (cần tracking theo SCD Type 2)

```python
changed_df = (
    source_df.alias("src")
    .join(
        target_df.filter("is_current = true").alias("tgt"),
        on="customer_id",
        how="inner"
    )
    .filter(
        (col("src.phone_number") != col("tgt.phone_number")) |
        (col("src.email") != col("tgt.email")) |
        (col("src.full_name") != col("tgt.full_name"))
    )
)
```

- Bước 2: Expire record hiện tại

```python
changed_df.createOrReplaceTempView("changed_df")

spark.sql("""
MERGE INTO gold.DimCustomer tgt
USING changed_df src
ON tgt.customer_id = src.customer_id
AND tgt.is_current = TRUE

WHEN MATCHED THEN
UPDATE SET
    tgt.effective_end_date = current_date(),
    tgt.is_current = FALSE
""")
```

- Bước 3: Insert version mới

```python
new_version_df = (
    changed_df
    .withColumn("effective_start_date", current_date())
    .withColumn(
        "effective_end_date",
        to_date(lit("9999-12-31"))
    )
    .withColumn("is_current", lit(True))
)

new_version_df.write.mode("append").saveAsTable("gold.DimCustomer")
```
- Bước 4: Update các column không cần tracking (Update theo SCD Type 1)

```python
changed_update_df = (
    source_df.alias("src")
    .join(
        target_df.filter("is_current = true").alias("tgt"),
        on="customer_id",
        how="inner"
    )
    .filter(
        (col("src.city") <> col("tgt.city")) |
        (col("src.district") <> col("tgt.district")) |
        -- Additional columns
    )
)

changed_update_df.createOrReplaceTempView("changed_update_df")

spark.sql("""
MERGE INTO gold.DimCustomer tgt
USING changed_update_df src
ON tgt.customer_id = src.customer_id
AND tgt.is_current = TRUE

WHEN MATCHED THEN
UPDATE SET
    tgt.city = src.city,
    tgt.district = src.district,
    -- Additional columns
""")
```

- Bước 5: Insert customer mới

```python
new_customer_df = (
    source_df.alias("src")
    .join(
        target_df.alias("tgt"),
        on="customer_id",
        how="left_anti"
    )
    .withColumn("effective_start_date", current_date())
    .withColumn(
        "effective_end_date",
        to_date(lit("9999-12-31"))
    )
    .withColumn("is_current", lit(True))
)

new_customer_df.write.mode("append").saveAsTable("gold.DimCustomer")
```
- Bước 6: Soft delete (nếu source là Full Snapshot)

```python
deleted_df = (
    target_df
    .filter("is_current = true")
    .alias("tgt")
    .join(
        source_df.alias("src"),
        on="customer_id",
        how="left_anti"
    )
)

deleted_df.createOrReplaceTempView("deleted_df")

spark.sql("""
MERGE INTO gold.DimCustomer tgt
USING deleted_df src
ON tgt.customer_id = src.customer_id
AND tgt.is_current = TRUE

WHEN MATCHED THEN
UPDATE SET
    tgt.effective_end_date = current_date(),
    tgt.is_current = FALSE
""")
```

### Notes

- Existing active records are expired by updating:
  - `effective_end_date`
  - `is_current = FALSE`
- A new version of the record is inserted with:
  - `effective_start_date = current_date()`
  - `effective_end_date = '9999-12-31'`
  - `is_current = TRUE`
- Historical records are retained for auditing and reporting purposes.