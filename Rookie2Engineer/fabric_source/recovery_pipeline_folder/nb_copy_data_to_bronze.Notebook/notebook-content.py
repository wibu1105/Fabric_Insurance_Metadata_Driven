# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "1abd17a2-112c-4390-a066-25015003935f",
# META       "default_lakehouse_name": "Rookie2Engineer_Lakehouse",
# META       "default_lakehouse_workspace_id": "5db1b4b5-9a8b-4bf9-808d-ed9af21bd9a8",
# META       "known_lakehouses": [
# META         {
# META           "id": "1abd17a2-112c-4390-a066-25015003935f"
# META         }
# META       ]
# META     },
# META     "warehouse": {
# META       "default_warehouse": "e013e43e-49e8-865d-4824-221f0cbc1668",
# META       "known_warehouses": [
# META         {
# META           "id": "e013e43e-49e8-865d-4824-221f0cbc1668",
# META           "type": "Datawarehouse"
# META         }
# META       ]
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

source_system = "payment_system"
source_schema = ""
source_table = "payment"
destination_schema = "bronze"
destination_table = "payment"
load_type = "incremental"
watermark_column = "last_updated" 
last_watermark_value = "1900-01-01"
table_id = "2005"
audit_session_id = ""
audit_table_session_id = ""
load_config_from_warehouse = "true"
audit_warehouse_name = "Rookie2Engineer_Warehouse"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
audit_warehouse_sql_endpoint = "3ukzqa5oadlurln3behjhxf4ae-ww2lcxmltl4uxaen5wnpeg6zva.datawarehouse.fabric.microsoft.com"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import pyspark.sql.functions as F
from pyspark.sql import SparkSession

try:
    import com.microsoft.spark.fabric  # type: ignore # noqa: F401
    from com.microsoft.spark.fabric.Constants import Constants  # type: ignore
except Exception:
    Constants = None

spark = SparkSession.builder.getOrCreate()

DEFAULT_AUDIT_WAREHOUSE_SQL_ENDPOINT = "3ukzqa5oadlurln3behjhxf4ae-ww2lcxmltl4uxaen5wnpeg6zva.datawarehouse.fabric.microsoft.com"


def blank(value):
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.upper() == "NULL"


def truthy(value):
    return str(value).strip().lower() in ("true", "1", "yes", "y")


def to_int(value, default=0):
    try:
        if blank(value):
            return default
        return int(float(str(value)))
    except Exception:
        return default


def warehouse_object(schema_name, table_name):
    if blank(audit_warehouse_name):
        raise ValueError("audit_warehouse_name is required")
    return f"{audit_warehouse_name}.{schema_name}.{table_name}"


def read_warehouse_table(schema_name, table_name):
    reader = spark.read
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            reader = reader.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            reader = reader.option(Constants.DatawarehouseId, audit_warehouse_id)
    return reader.synapsesql(warehouse_object(schema_name, table_name))


def sql_literal(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def execute_warehouse_sql(sql_text):
    endpoint_value = globals().get("audit_warehouse_sql_endpoint", DEFAULT_AUDIT_WAREHOUSE_SQL_ENDPOINT)
    if blank(endpoint_value):
        raise ValueError("audit_warehouse_sql_endpoint is required to update Warehouse watermark tables")

    try:
        token = notebookutils.credentials.getToken("https://database.windows.net/")
    except NameError:
        token = mssparkutils.credentials.getToken("https://database.windows.net/")

    jvm = spark._sc._gateway.jvm
    props = jvm.java.util.Properties()
    props.setProperty("accessToken", token)
    props.setProperty("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")

    jdbc_url = (
        f"jdbc:sqlserver://{endpoint_value}:1433;"
        f"database={audit_warehouse_name};"
        "encrypt=true;"
        "trustServerCertificate=false;"
        "hostNameInCertificate=*.datawarehouse.fabric.microsoft.com;"
        "loginTimeout=30;"
    )

    conn = None
    stmt = None
    try:
        conn = jvm.java.sql.DriverManager.getConnection(jdbc_url, props)
        stmt = conn.createStatement()
        stmt.execute(sql_text)
    finally:
        if stmt is not None:
            stmt.close()
        if conn is not None:
            conn.close()


def exit_notebook(value):
    out = "" if value is None else str(value)
    try:
        notebookutils.notebook.exit(out)
    except NameError:
        mssparkutils.notebook.exit(out)


def apply_config_from_warehouse():
    global source_system, source_schema, source_table, destination_schema, destination_table, load_type, watermark_column

    if blank(table_id):
        print("table_id is blank, using notebook parameters instead of Warehouse config.")
        return

    cfg_rows = (
        read_warehouse_table("cfg", "cfg_landing_bronze_table")
        .where(F.col("table_id") == to_int(table_id))
        .limit(1)
        .collect()
    )

    if not cfg_rows:
        print(f"No Warehouse config found for table_id {table_id}. Using notebook parameters.")
        return

    cfg = cfg_rows[0].asDict(recursive=True)
    if not truthy(cfg.get("is_active", True)):
        raise ValueError(f"Warehouse config table_id {table_id} is inactive")

    cfg_destination_schema = "" if cfg.get("destination_schema") is None else str(cfg.get("destination_schema"))
    if cfg_destination_schema.lower() != "bronze":
        raise ValueError(f"Warehouse config table_id {table_id} is for destination_schema='{cfg_destination_schema}', expected 'bronze'")

    source_system = "" if cfg.get("source_system") is None else str(cfg.get("source_system"))
    source_schema = "" if cfg.get("source_schema") is None else str(cfg.get("source_schema"))
    source_table = "" if cfg.get("source_table") is None else str(cfg.get("source_table"))
    destination_schema = cfg_destination_schema
    destination_table = str(cfg.get("destination_table") or source_table)
    load_type = str(cfg.get("load_type") or load_type).strip().lower()
    watermark_column = str(cfg.get("source_watermark_column") or watermark_column or "").strip()

    print(f"Loaded Bronze config from Warehouse for table_id {table_id}: {destination_schema}.{destination_table}")


def get_last_watermark(table_id):
    wm_rows = (
        read_warehouse_table("cfg", "cfg_table_watermark")
        .where(F.col("table_id") == to_int(table_id))
        .select(F.col("last_watermark_value").cast("string").alias("last_watermark_value"))
        .limit(1)
        .collect()
    )

    if not wm_rows:
        return "1900-01-01"

    value = wm_rows[0]["last_watermark_value"]
    return "1900-01-01" if blank(value) else str(value)


if truthy(globals().get("load_config_from_warehouse", "true")):
    apply_config_from_warehouse()

if blank(source_schema):
    source_schema = None

load_type = str(load_type).strip().lower()
if blank(destination_schema):
    destination_schema = "bronze"
if blank(destination_table):
    destination_table = source_table

# 1. READ LOGIC & COLUMN ASSIGNMENT
if source_schema is None:
    full_load_date_col = "batch_date"

    base_landing_path = f"Files/landing/{source_system}/{source_table}/"
    df_landing = spark.read \
        .option("multiline", "true") \
        .option("basePath", base_landing_path) \
        .json(f"{base_landing_path}*/*.json")

    print(f"Reading JSON from {base_landing_path}")

    destination_table_name_temp = f"{destination_schema}.{destination_table}"
    try:
        target_schema = spark.table(destination_table_name_temp).schema
        for field in target_schema:
            if field.name in df_landing.columns:
                df_landing = df_landing.withColumn(field.name, F.col(field.name).cast(field.dataType))
        print(f"Casted JSON columns to match Bronze schema for '{destination_table_name_temp}'")
    except Exception as e:
        print(f"Warning: Could not read target schema for casting: {e}. Proceeding with inferred types.")

else:
    full_load_date_col = "_etl_date"

    landing_path = f"{source_schema}.{source_table}"
    df_landing = spark.table(landing_path)
    print(f"Reading Table from {landing_path}")

# RETRIEVE WATERMARK FROM WAREHOUSE
last_watermark_value = "1900-01-01"

if load_type == "incremental":
    if blank(watermark_column):
        raise ValueError("watermark_column/source_watermark_column is required for incremental load")

    last_watermark_value = get_last_watermark(table_id)
    print(f"Retrieved Warehouse watermark for table_id {table_id}: {last_watermark_value}")

# 2. FILTER LOGIC
if load_type == "incremental":
    df_filtered = df_landing.filter(F.col(watermark_column) > last_watermark_value)
    print(f"Applying Incremental Filter: {watermark_column} > {last_watermark_value}")

elif load_type == "full":
    max_date_row = df_landing.select(F.max(full_load_date_col)).collect()[0][0]

    if max_date_row:
        df_filtered = df_landing.filter(F.col(full_load_date_col) == max_date_row)
        print(f"Applying Full Load Filter: {full_load_date_col} = {max_date_row}")
    else:
        df_filtered = df_landing

else:
    raise ValueError(f"Unsupported load_type: {load_type}")

processed_rows = df_filtered.count()

# 2.5 DROP SQL METADATA COLUMNS
if source_schema is not None:
    cols_to_drop = ["_etl_date", "_etl_audit_session_id", "_etl_audit_table_session_id"]
    df_filtered = df_filtered.drop(*cols_to_drop)
    print(f"Dropped SQL metadata columns: {cols_to_drop}")

# 3. WRITE LOGIC: Save to Bronze Lakehouse
destination_table_name = f"{destination_schema}.{destination_table}"
write_mode = "append" if load_type == "incremental" else "overwrite"

df_filtered.write \
    .format("delta") \
    .mode(write_mode) \
    .saveAsTable(destination_table_name)

print(f"Successfully wrote data to {destination_table_name} using {write_mode} mode.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def update_watermark_in_warehouse(table_id, watermark_column, df_filtered):
    max_val_row = df_filtered.select(F.max(watermark_column)).collect()[0][0]

    if not max_val_row:
        print("No new records were found during this incremental run. Watermark remains unchanged.")
        return None

    table_id_int = to_int(table_id)
    max_val_str = str(max_val_row)
    session_id = globals().get("audit_session_id", "") or globals().get("audit_table_session_id", "")

    update_sql = f"""
DECLARE @table_id INT = {table_id_int};
DECLARE @new_watermark DATETIME2(6) = TRY_CAST({sql_literal(max_val_str)} AS DATETIME2(6));
DECLARE @audit_session_id VARCHAR(100) = {sql_literal(session_id)};

IF @table_id IS NOT NULL AND @new_watermark IS NOT NULL
BEGIN
    IF EXISTS (SELECT 1 FROM cfg.cfg_table_watermark WHERE table_id = @table_id)
    BEGIN
        UPDATE cfg.cfg_table_watermark
        SET
            last_watermark_value = @new_watermark,
            last_audit_session = @audit_session_id,
            last_load_time = SYSUTCDATETIME(),
            updated_date = SYSUTCDATETIME()
        WHERE table_id = @table_id;
    END
    ELSE
    BEGIN
        INSERT INTO cfg.cfg_table_watermark (
            table_id,
            last_watermark_value,
            last_audit_session,
            last_load_time,
            created_date,
            updated_date
        )
        VALUES (
            @table_id,
            @new_watermark,
            @audit_session_id,
            SYSUTCDATETIME(),
            SYSUTCDATETIME(),
            SYSUTCDATETIME()
        );
    END;
END;
"""

    execute_warehouse_sql(update_sql)
    print(f"Successfully updated Warehouse watermark for table_id {table_id_int} to {max_val_str}")
    return max_val_str


# 4. UPDATE WATERMARK IN WAREHOUSE
if load_type == "incremental":
    update_watermark_in_warehouse(table_id, watermark_column, df_filtered)

print(f"Total rows processed: {processed_rows}")
exit_notebook(str(processed_rows))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
