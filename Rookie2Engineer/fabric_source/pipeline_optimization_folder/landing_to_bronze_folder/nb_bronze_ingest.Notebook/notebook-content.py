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

# Parameters
audit_session_id = ""
rows = ""
fail_fast = "true"
audit_sink = "warehouse"
audit_warehouse_name = "Rookie2Engineer_Warehouse"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
audit_warehouse_sql_endpoint = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
from datetime import datetime

import pyspark.sql.functions as F
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType

try:
    import com.microsoft.spark.fabric  # type: ignore # noqa: F401
    from com.microsoft.spark.fabric.Constants import Constants  # type: ignore
except Exception:
    Constants = None

spark = SparkSession.builder.getOrCreate()

DEFAULT_AUDIT_WAREHOUSE_SQL_ENDPOINT = "3ukzqa5oadlurln3behjhxf4ae-ww2lcxmltl4uxaen5wnpeg6zva.datawarehouse.fabric.microsoft.com"

AUDIT_TABLE_SESSION_SCHEMA = StructType([
    StructField("audit_table_session_id", StringType(), False),
    StructField("audit_session_id", StringType(), True),
    StructField("table_id", IntegerType(), True),
    StructField("layer_name", StringType(), True),
    StructField("load_type", StringType(), True),
    StructField("status", StringType(), True),
    StructField("start_time", TimestampType(), True),
    StructField("end_time", TimestampType(), True),
    StructField("processed_rows", IntegerType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("updated_at", TimestampType(), True),
])

AUDIT_ERROR_SCHEMA = StructType([
    StructField("audit_error_id", StringType(), False),
    StructField("audit_table_session_id", StringType(), True),
    StructField("step_name", StringType(), True),
    StructField("error_code", StringType(), True),
    StructField("error_name", StringType(), True),
    StructField("error_time", TimestampType(), True),
])


def blank(value):
    return value is None or str(value).strip() == ""


def truthy(value):
    return str(value).strip().lower() in ("true", "1", "yes", "y")


def to_int(value, default=0):
    try:
        if blank(value):
            return default
        return int(float(str(value)))
    except Exception:
        return default


def utc_now():
    return datetime.utcnow()


def exit_notebook(value):
    out = "" if value is None else str(value)
    try:
        notebookutils.notebook.exit(out)
    except NameError:
        mssparkutils.notebook.exit(out)


def use_warehouse_audit():
    return str(audit_sink).strip().lower() == "warehouse"


def warehouse_object(schema_name, table_name):
    if blank(audit_warehouse_name):
        raise ValueError("audit_warehouse_name is required when audit_sink = 'warehouse'")
    return f"{audit_warehouse_name}.{schema_name}.{table_name}"


def read_warehouse_table(schema_name, table_name):
    reader = spark.read
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            reader = reader.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            reader = reader.option(Constants.DatawarehouseId, audit_warehouse_id)
    return reader.synapsesql(warehouse_object(schema_name, table_name))


def write_warehouse_table(df, schema_name, table_name, mode="append"):
    writer = df.write.mode(mode)
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            writer = writer.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            writer = writer.option(Constants.DatawarehouseId, audit_warehouse_id)
    writer.synapsesql(warehouse_object(schema_name, table_name))


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


def append_table_session_result(audit_table_session_id, table_id, load_type, status, start_time, end_time, processed_rows=0):
    audit_df = spark.createDataFrame(
        [{
            "audit_table_session_id": audit_table_session_id,
            "audit_session_id": audit_session_id,
            "table_id": to_int(table_id),
            "layer_name": "bronze",
            "load_type": "" if load_type is None else str(load_type),
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "processed_rows": to_int(processed_rows),
            "created_at": start_time,
            "updated_at": end_time,
        }],
        schema=AUDIT_TABLE_SESSION_SCHEMA,
    )
    if use_warehouse_audit():
        write_warehouse_table(audit_df, "audit", "audit_table_session_log")
    else:
        audit_df.write.format("delta").mode("append").saveAsTable("audit.audit_table_session_log")


def append_error_log(audit_table_session_id, error_code, error_message):
    safe_error = str(error_message).replace("|", " ").replace("\r", " ").replace("\n", " ")
    audit_df = spark.createDataFrame(
        [{
            "audit_error_id": str(uuid.uuid4()),
            "audit_table_session_id": audit_table_session_id,
            "step_name": "NB_BRONZE_REPLACE_FOREACH",
            "error_code": error_code,
            "error_name": safe_error,
            "error_time": utc_now(),
        }],
        schema=AUDIT_ERROR_SCHEMA,
    )
    if use_warehouse_audit():
        write_warehouse_table(audit_df, "audit", "audit_error_log")
    else:
        audit_df.write.format("delta").mode("append").saveAsTable("audit.audit_error_log")


def normalize_rows(raw_rows):
    if blank(raw_rows):
        return []
    if isinstance(raw_rows, list):
        return raw_rows
    if isinstance(raw_rows, dict):
        value = raw_rows.get("value")
        return value if isinstance(value, list) else [raw_rows]
    parsed = json.loads(str(raw_rows).strip())
    if isinstance(parsed, dict):
        value = parsed.get("value")
        return value if isinstance(value, list) else [parsed]
    return parsed


def get_last_watermark(table_id):
    table_id_int = to_int(table_id)
    if use_warehouse_audit():
        wm_df = (
            read_warehouse_table("cfg", "cfg_table_watermark")
            .where(F.col("table_id") == table_id_int)
            .select(F.col("last_watermark_value").cast("string").alias("last_watermark_value"))
            .limit(1)
        )
    else:
        wm_df = spark.sql(f"""
            SELECT CAST(last_watermark_value AS STRING) AS last_watermark_value
            FROM cfg.cfg_table_watermark
            WHERE table_id = {table_id_int}
            LIMIT 1
        """)

    rows_found = wm_df.collect()
    if not rows_found:
        return "1900-01-01"
    value = rows_found[0]["last_watermark_value"]
    return "1900-01-01" if value is None or str(value).strip() == "" else str(value)


def update_watermark(table_id, watermark_column, audit_table_session_id, df_filtered):
    max_val_row = df_filtered.select(F.max(watermark_column)).collect()[0][0]
    if not max_val_row:
        print("No new records were found during this incremental run. Watermark remains unchanged.")
        return None

    table_id_int = to_int(table_id)
    max_val_str = str(max_val_row)

    if use_warehouse_audit():
        update_sql = f"""
DECLARE @table_id INT = {table_id_int};
DECLARE @new_watermark DATETIME2(6) = TRY_CAST({sql_literal(max_val_str)} AS DATETIME2(6));
DECLARE @audit_session_id VARCHAR(100) = {sql_literal(audit_session_id)};

IF @table_id IS NOT NULL AND @new_watermark IS NOT NULL
BEGIN
    IF EXISTS (SELECT 1 FROM cfg.cfg_table_watermark WHERE table_id = @table_id)
    BEGIN
        UPDATE cfg.cfg_table_watermark
        SET
            last_watermark_value = @new_watermark,
            last_audit_session = @audit_session_id,
            last_load_time = CURRENT_TIMESTAMP,
            updated_date = CURRENT_TIMESTAMP
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
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END;
END;
"""
        execute_warehouse_sql(update_sql)
        print(f"Successfully updated Warehouse watermark for table_id {table_id_int} to {max_val_str}")
        return max_val_str

    merge_sql = f"""
    MERGE INTO cfg.cfg_table_watermark AS target
    USING (
        SELECT
            {table_id_int} AS table_id,
            CAST({sql_literal(max_val_str)} AS TIMESTAMP) AS new_watermark,
            {sql_literal(audit_session_id)} AS session_id
    ) AS source
    ON target.table_id = source.table_id
    WHEN MATCHED THEN
        UPDATE SET
            last_watermark_value = source.new_watermark,
            last_audit_session = source.session_id,
            last_load_time = current_timestamp(),
            updated_date = current_timestamp()
    WHEN NOT MATCHED THEN
        INSERT (
            table_id,
            last_watermark_value,
            last_audit_session,
            last_load_time,
            created_date,
            updated_date
        )
        VALUES (
            source.table_id,
            source.new_watermark,
            source.session_id,
            current_timestamp(),
            current_timestamp(),
            current_timestamp()
        )
    """
    spark.sql(merge_sql)
    print(f"Successfully updated Lakehouse watermark for table_id {table_id_int} to {max_val_str}")
    return max_val_str


def copy_one_table(cfg):
    table_id = str(cfg.get("table_id", ""))
    source_system = str(cfg.get("source_system", ""))
    source_schema = "" if cfg.get("source_schema") is None else str(cfg.get("source_schema", ""))
    source_table = str(cfg.get("source_table", ""))
    load_type = str(cfg.get("load_type", "")).lower()
    watermark_column = "" if cfg.get("source_watermark_column") is None else str(cfg.get("source_watermark_column", ""))
    audit_table_session_id = str(cfg.get("audit_table_session_id") or uuid.uuid4())
    start_time = utc_now()

    if (source_schema and source_schema.upper() == "NULL") or source_schema == "":
        source_schema = None

    if source_schema is None:
        full_load_date_col = "batch_date"
        base_landing_path = f"Files/landing/{source_system}/{source_table}/"
        df_landing = (
            spark.read
            .option("multiline", "true")
            .option("basePath", base_landing_path)
            .json(f"{base_landing_path}*/*.json")
        )
        print(f"Reading JSON from {base_landing_path}")

        destination_table_name_temp = f"bronze.{source_table}"
        try:
            target_schema = spark.table(destination_table_name_temp).schema
            for field in target_schema:
                if field.name in df_landing.columns:
                    df_landing = df_landing.withColumn(field.name, F.col(field.name).cast(field.dataType))
            print(f"Casted JSON columns to match Bronze schema for '{destination_table_name_temp}'")
        except Exception as exc:
            print(f"Warning: Could not read target schema for casting: {exc}. Proceeding with inferred types.")
    else:
        full_load_date_col = "_etl_date"
        landing_path = f"{source_schema}.{source_table}"
        df_landing = spark.table(landing_path)
        print(f"Reading table from {landing_path}")

    if load_type == "incremental":
        last_watermark_value = get_last_watermark(table_id)
        print(f"Retrieved watermark for table {table_id}: {last_watermark_value}")
        df_filtered = df_landing.filter(F.col(watermark_column) > last_watermark_value)
        print(f"Applying incremental filter: {watermark_column} > {last_watermark_value}")
    elif load_type == "full":
        max_date_row = df_landing.select(F.max(full_load_date_col)).collect()[0][0]
        if max_date_row:
            df_filtered = df_landing.filter(F.col(full_load_date_col) == max_date_row)
            print(f"Applying full load filter: {full_load_date_col} = {max_date_row}")
        else:
            df_filtered = df_landing
    else:
        raise ValueError(f"Unsupported load_type: {load_type}")

    processed_rows = df_filtered.count()

    if source_schema is not None:
        cols_to_drop = ["_etl_date", "_etl_audit_session_id", "_etl_audit_table_session_id"]
        df_filtered = df_filtered.drop(*cols_to_drop)
        print(f"Dropped SQL metadata columns: {cols_to_drop}")

    destination_table_name = f"bronze.{source_table}"
    write_mode = "append" if load_type == "incremental" else "overwrite"
    (
        df_filtered.write
        .format("delta")
        .mode(write_mode)
        .saveAsTable(destination_table_name)
    )
    print(f"Successfully wrote data to {destination_table_name} using {write_mode} mode.")

    max_watermark_value = None
    if load_type == "incremental":
        max_watermark_value = update_watermark(table_id, watermark_column, audit_table_session_id, df_filtered)

    end_time = utc_now()
    append_table_session_result(
        audit_table_session_id=audit_table_session_id,
        table_id=table_id,
        load_type=load_type,
        status="success",
        start_time=start_time,
        end_time=end_time,
        processed_rows=processed_rows,
    )

    return {
        "table_id": to_int(table_id),
        "source_table": source_table,
        "status": "success",
        "processed_rows": processed_rows,
        "audit_table_session_id": audit_table_session_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "max_watermark_value": max_watermark_value,
    }


def run_all_table():
    if blank(audit_session_id):
        raise ValueError("audit_session_id is required")

    configs = normalize_rows(rows)
    if not configs:
        exit_notebook(json.dumps({"status": "success", "message": "No bronze rows from Filter"}, default=str))

    results = []
    for raw_cfg in configs:
        cfg = raw_cfg.asDict(recursive=True) if hasattr(raw_cfg, "asDict") else dict(raw_cfg)
        if str(cfg.get("destination_schema", "")).lower() != "bronze" or not truthy(cfg.get("is_active", True)):
            continue

        table_start = utc_now()
        audit_table_session_id = str(uuid.uuid4())
        cfg["audit_table_session_id"] = audit_table_session_id
        try:
            result = copy_one_table(cfg)
            results.append(result)
        except Exception as exc:
            table_id = cfg.get("table_id", "")
            load_type = cfg.get("load_type", "")
            error_message = str(exc)
            append_table_session_result(
                audit_table_session_id=audit_table_session_id,
                table_id=table_id,
                load_type=load_type,
                status="failed",
                start_time=table_start,
                end_time=utc_now(),
                processed_rows=0,
            )
            append_error_log(audit_table_session_id, "COPY ERROR", error_message)
            results.append({
                "table_id": to_int(table_id),
                "source_table": cfg.get("source_table"),
                "status": "failed",
                "processed_rows": 0,
                "audit_table_session_id": audit_table_session_id,
                "error": error_message,
            })
            if truthy(fail_fast):
                break

    final_status = "failed" if any(item["status"] != "success" for item in results) else "success"
    output = {"status": final_status, "tables": results}
    if final_status != "success":
        raise RuntimeError(json.dumps(output, default=str))
    exit_notebook(json.dumps(output, default=str))


run_all_table()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
