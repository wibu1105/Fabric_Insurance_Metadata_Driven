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
audit_batch_id = ""
audit_session_id = ""
pipeline_name = "pl_bronze_to_silver"
triggered_by = ""
target_tables = ""
rows = ""
is_recovery = "false"
max_parallel_workers = "3"
force_dependency_overrides = "true"
fail_fast = "true"
manage_session_audit = "false"
audit_sink = "warehouse"
audit_warehouse_name = "Rookie2Engineer_Warehouse"
audit_warehouse_workspace_id = ""
audit_warehouse_id = ""
child_notebook_folder = ""
child_workspace = ""
dag_timeout_seconds = "43200"
timeout_per_cell_seconds = "3600"
retry = "0"
retry_interval_seconds = "30"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
from datetime import datetime

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType
from pyspark.sql.window import Window

try:
    import com.microsoft.spark.fabric  # type: ignore # noqa: F401
    from com.microsoft.spark.fabric.Constants import Constants  # type: ignore
except Exception:
    Constants = None

spark = SparkSession.builder.getOrCreate()

DEFAULT_AUDIT_WAREHOUSE_SQL_ENDPOINT = "3ukzqa5oadlurln3behjhxf4ae-ww2lcxmltl4uxaen5wnpeg6zva.datawarehouse.fabric.microsoft.com"

TABLE_DEPENDENCIES = {
    "customers": [],
    "agents": [],
    "insurance_providers": [],
    "vehicle": ["customers"],
    "quotation": ["customers", "agents", "insurance_providers"],
    "quotation_item": ["quotation"],
    "policy": ["quotation"],
    "payment": ["policy"],
    "cancellation": ["policy"],
}

DEPENDENCY_OVERRIDES = {
    "customers": 1,
    "agents": 1,
    "insurance_providers": 1,
    "vehicle": 2,
    "quotation": 2,
    "quotation_item": 3,
    "policy": 3,
    "payment": 4,
    "cancellation": 4,
}

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


def normalize_status(value):
    text = str(value or "").strip().lower()
    if text in ("success", "succeeded"):
        return "Succeeded"
    if text in ("fail", "failed", "failure"):
        return "Failed"
    if text == "skipped":
        return "Skipped"
    return str(value or "Failed").strip() or "Failed"


def is_success_status(value):
    return normalize_status(value) == "Succeeded"


def utc_now():
    return datetime.utcnow()


def parse_ts(value, fallback):
    if blank(value):
        return fallback
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return fallback


def exit_notebook(value):
    out = "" if value is None else str(value)
    try:
        notebookutils.notebook.exit(out)
    except NameError:
        mssparkutils.notebook.exit(out)


def get_notebookutils():
    try:
        return notebookutils
    except NameError:
        return mssparkutils


def use_warehouse_audit():
    return str(audit_sink).strip().lower() == "warehouse"


def warehouse_object(schema_name, table_name):
    if blank(audit_warehouse_name):
        raise ValueError("audit_warehouse_name is required when audit_sink = 'warehouse'")
    return f"{audit_warehouse_name}.{schema_name}.{table_name}"


def warehouse_table(table_name):
    return warehouse_object("audit", table_name)


def sql_literal(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("'", "''") + "'"


def read_warehouse_table(schema_name, table_name):
    reader = spark.read
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            reader = reader.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            reader = reader.option(Constants.DatawarehouseId, audit_warehouse_id)
    return reader.synapsesql(warehouse_object(schema_name, table_name))


def write_warehouse_table(df, table_name, mode="append"):
    writer = df.write.mode(mode)
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            writer = writer.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            writer = writer.option(Constants.DatawarehouseId, audit_warehouse_id)
    writer.synapsesql(warehouse_table(table_name))


def execute_warehouse_sql(sql_text):
    endpoint = globals().get("audit_warehouse_sql_endpoint", DEFAULT_AUDIT_WAREHOUSE_SQL_ENDPOINT)
    if blank(endpoint):
        raise ValueError("audit_warehouse_sql_endpoint is required to update Warehouse audit tables from recovery mode")

    try:
        token = notebookutils.credentials.getToken("https://database.windows.net/")
    except NameError:
        token = mssparkutils.credentials.getToken("https://database.windows.net/")

    jvm = spark._sc._gateway.jvm
    props = jvm.java.util.Properties()
    props.setProperty("accessToken", token)
    props.setProperty("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver")

    jdbc_url = (
        f"jdbc:sqlserver://{endpoint}:1433;"
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
            "layer_name": "silver",
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
        write_warehouse_table(audit_df, "audit_table_session_log")
    else:
        audit_df.write.format("delta").mode("append").saveAsTable("audit.audit_table_session_log")


def update_table_session_result(audit_table_session_id, status, processed_rows=0):
    action = "success" if is_success_status(status) else "failed"

    if use_warehouse_audit():
        execute_warehouse_sql(f"""
        EXEC audit.sp_audit_table_session_log
            @action = {sql_literal(action)},
            @audit_table_session_id = {sql_literal(audit_table_session_id)},
            @processed_rows = {to_int(processed_rows)};
        """)
        return

    if action == "success":
        spark.sql(f"""
        UPDATE audit.audit_table_session_log
        SET
            status = 'success',
            end_time = current_timestamp(),
            updated_at = current_timestamp(),
            processed_rows = {to_int(processed_rows)}
        WHERE audit_table_session_id = {sql_literal(audit_table_session_id)}
        """)
    else:
        spark.sql(f"""
        UPDATE audit.audit_table_session_log
        SET
            status = 'failed',
            end_time = current_timestamp(),
            updated_at = current_timestamp()
        WHERE audit_table_session_id = {sql_literal(audit_table_session_id)}
        """)


def append_error_log(audit_table_session_id, error_code, error_message):
    message = error_message if not blank(error_message) else f"{error_code}: silver table failed without an error message"
    safe_error = str(message).replace("|", " ").replace("\r", " ").replace("\n", " ")
    audit_df = spark.createDataFrame(
        [{
            "audit_error_id": str(uuid.uuid4()),
            "audit_table_session_id": audit_table_session_id,
            "step_name": "RUN SILVER RUNMULTIPLE PARENT",
            "error_code": error_code,
            "error_name": safe_error,
            "error_time": utc_now(),
        }],
        schema=AUDIT_ERROR_SCHEMA,
    )
    if use_warehouse_audit():
        write_warehouse_table(audit_df, "audit_error_log")
    else:
        audit_df.write.format("delta").mode("append").saveAsTable("audit.audit_error_log")


def normalize_rows(raw_rows):
    if blank(raw_rows):
        return None
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


def load_normal_config_from_warehouse():
    if use_warehouse_audit():
        return (
            read_warehouse_table("cfg", "cfg_silver_gold_table")
            .where(F.lower(F.col("layer_name")) == "silver")
            .select(
                "table_id",
                "layer_name",
                "target_schema",
                "target_table",
                "primary_key_column",
                "watermark_column",
                "notebook_name",
                "load_type",
                "dependency_level",
                "is_active",
            )
            .collect()
        )

    cfg_df = spark.table("cfg.cfg_silver_gold_table")
    cfg_columns = {field.name.lower() for field in cfg_df.schema.fields}
    is_active_expr = "is_active" if "is_active" in cfg_columns else "true AS is_active"
    return spark.sql(f"""
        SELECT
            table_id,
            layer_name,
            target_schema,
            target_table,
            primary_key_column,
            watermark_column,
            notebook_name,
            load_type,
            dependency_level,
            {is_active_expr}
        FROM cfg.cfg_silver_gold_table
        WHERE lower(layer_name) = 'silver'
    """).collect()


def load_recovery_config_from_warehouse():
    if not use_warehouse_audit():
        raise ValueError("Recovery mode currently requires audit_sink = 'warehouse'")
    if blank(audit_batch_id):
        raise ValueError("Recovery mode requires audit_batch_id")

    atsl = read_warehouse_table("audit", "audit_table_session_log")
    asl = read_warehouse_table("audit", "audit_session_log").alias("asl")
    abl = read_warehouse_table("audit", "audit_batch_log").alias("abl")
    csgt = read_warehouse_table("cfg", "cfg_silver_gold_table").alias("csgt")

    latest_window = Window.partitionBy("audit_table_session_id").orderBy(
        F.col("updated_at").desc_nulls_last(),
        F.col("end_time").desc_nulls_last(),
        F.col("start_time").desc_nulls_last(),
    )
    latest_atsl = (
        atsl
        .withColumn("rn", F.row_number().over(latest_window))
        .where(F.col("rn") == 1)
        .alias("atsl")
    )

    return (
        latest_atsl
        .join(asl, F.col("atsl.audit_session_id") == F.col("asl.audit_session_id"))
        .join(abl, F.col("abl.audit_batch_id") == F.col("asl.audit_batch_id"))
        .join(csgt, F.col("csgt.table_id") == F.col("atsl.table_id"))
        .where(F.col("abl.audit_batch_id") == str(audit_batch_id))
        .where(~F.lower(F.trim(F.col("atsl.status"))).isin("success", "succeeded"))
        .where(F.lower(F.col("atsl.layer_name")) == "silver")
        .where(F.lower(F.col("csgt.layer_name")) == "silver")
        .where(F.lower(F.col("csgt.is_active").cast("string")).isin("true", "1"))
        .select(
            F.col("atsl.audit_session_id"),
            F.col("atsl.audit_table_session_id"),
            F.col("csgt.table_id"),
            F.col("csgt.layer_name"),
            F.col("csgt.target_schema"),
            F.col("csgt.target_table"),
            F.col("csgt.primary_key_column"),
            F.col("csgt.watermark_column"),
            F.col("csgt.notebook_name"),
            F.col("csgt.load_type"),
            F.col("csgt.dependency_level"),
            F.col("csgt.is_active"),
        )
        .collect()
    )


def load_silver_config():
    selected_tables = {
        item.strip().lower()
        for item in str(target_tables or "").split(",")
        if item.strip()
    }

    input_rows = normalize_rows(rows)
    if input_rows is None:
        if truthy(is_recovery):
            input_rows = load_recovery_config_from_warehouse()
        else:
            input_rows = load_normal_config_from_warehouse()

    configs = []
    seen_tables = set()
    for row in input_rows:
        item = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        table_name = str(item["target_table"]).lower()
        if table_name not in TABLE_DEPENDENCIES:
            print(f"Skipping unsupported silver table: {table_name}")
            continue
        if selected_tables and table_name not in selected_tables:
            continue
        if table_name in seen_tables:
            print(f"Skipping duplicate silver table config: {table_name}")
            continue
        if not truthy(item.get("is_active", True)):
            continue
        if truthy(force_dependency_overrides):
            item["dependency_level"] = DEPENDENCY_OVERRIDES.get(table_name, to_int(item.get("dependency_level"), 99))
        item["target_table"] = table_name
        item["target_schema"] = item.get("target_schema", "silver") or "silver"
        if blank(item.get("audit_table_session_id")):
            if truthy(is_recovery):
                raise ValueError(f"Recovery mode requires audit_table_session_id for table {table_name}")
            item["audit_table_session_id"] = str(uuid.uuid4())
        else:
            item["audit_table_session_id"] = str(item["audit_table_session_id"])
        configs.append(item)
        seen_tables.add(table_name)

    return sorted(configs, key=lambda x: (to_int(x.get("dependency_level"), 99), to_int(x.get("table_id"), 0)))


def child_path(table_name):
    notebook_name = f"nb_child_{table_name}"
    folder = str(child_notebook_folder or "").strip().strip("/")
    return f"{folder}/{notebook_name}" if folder else notebook_name


def build_dag(configs):
    active_tables = {str(cfg["target_table"]).lower() for cfg in configs}
    activities = []
    for cfg in configs:
        table_name = str(cfg["target_table"]).lower()
        activity = {
            "name": table_name,
            "path": child_path(table_name),
            "timeoutPerCellInSeconds": to_int(timeout_per_cell_seconds, 3600),
            "retry": to_int(retry, 0),
            "retryIntervalInSeconds": to_int(retry_interval_seconds, 30),
            "args": {
                "audit_session_id": audit_session_id,
                "audit_table_session_id": cfg["audit_table_session_id"],
                "table_id": str(cfg.get("table_id", "")),
                "load_type": str(cfg.get("load_type", "")),
                "target_schema": str(cfg.get("target_schema", "silver")),
                "target_table": table_name,
                "audit_sink": audit_sink,
                "audit_warehouse_name": audit_warehouse_name,
                "audit_warehouse_workspace_id": audit_warehouse_workspace_id,
                "audit_warehouse_id": audit_warehouse_id,
                "useRootDefaultLakehouse": True,
            },
        }
        dependencies = [dep for dep in TABLE_DEPENDENCIES.get(table_name, []) if dep in active_tables]
        if dependencies:
            activity["dependencies"] = dependencies
        if not blank(child_workspace):
            activity["workspace"] = child_workspace
        activities.append(activity)

    return {
        "activities": activities,
        "timeoutInSeconds": to_int(dag_timeout_seconds, 43200),
        "concurrency": max(1, to_int(max_parallel_workers, 3)),
    }


def parse_exit_payload(exit_val):
    if blank(exit_val):
        return {}
    try:
        return json.loads(str(exit_val))
    except Exception:
        return {"raw_exitVal": str(exit_val)}


def run_parent():
    global audit_session_id, audit_batch_id

    if truthy(manage_session_audit):
        raise ValueError("manage_session_audit must be false. Use pipeline Script activities for session start/end.")

    configs = load_silver_config()
    if not configs:
        exit_notebook(json.dumps({"status": "success", "message": "No active silver tables"}, default=str))

    if truthy(is_recovery):
        recovery_session_ids = {
            str(cfg.get("audit_session_id")).strip()
            for cfg in configs
            if not blank(cfg.get("audit_session_id"))
        }
        if blank(audit_session_id):
            if len(recovery_session_ids) != 1:
                raise ValueError(f"Recovery mode expects exactly one audit_session_id, got {len(recovery_session_ids)}")
            audit_session_id = next(iter(recovery_session_ids))
    elif blank(audit_session_id):
        audit_session_id = str(uuid.uuid4())

    if blank(audit_batch_id):
        audit_batch_id = audit_session_id

    dag = build_dag(configs)
    print(json.dumps(dag, indent=2, default=str))

    utils = get_notebookutils()
    utils.notebook.validateDAG(dag)

    parent_start = utc_now()
    runmultiple_failed = None
    try:
        raw_results = utils.notebook.runMultiple(dag, {"displayDAGViaGraphviz": False})
    except Exception as exc:
        if hasattr(exc, "result"):
            raw_results = exc.result
            runmultiple_failed = exc
        else:
            raise

    table_results = []
    now_after_run = utc_now()
    for cfg in configs:
        table_name = str(cfg["target_table"]).lower()
        activity_result = raw_results.get(table_name) if isinstance(raw_results, dict) else None
        audit_table_session_id = cfg["audit_table_session_id"]
        table_id = cfg.get("table_id", "")
        load_type = cfg.get("load_type", "")

        status = "Skipped"
        processed_rows = 0
        error_message = "Activity was not executed, likely because an upstream dependency failed."
        start_time = parent_start
        end_time = now_after_run
        payload = {}

        if activity_result is not None:
            exception = activity_result.get("exception") if isinstance(activity_result, dict) else None
            if exception:
                status = "Failed"
                error_message = str(exception)
            else:
                payload = parse_exit_payload(activity_result.get("exitVal", ""))
                status = normalize_status(payload.get("status", "Succeeded"))
                processed_rows = to_int(payload.get("processed_rows", 0))
                payload_table_id = payload.get("table_id")
                if to_int(payload_table_id, 0) > 0:
                    table_id = payload_table_id
                start_time = parse_ts(payload.get("start_time"), parent_start)
                end_time = parse_ts(payload.get("end_time"), now_after_run)
                error_message = payload.get("error", "")

        audit_status = (
            "success"
            if is_success_status(status)
            else "failed"
            if normalize_status(status) == "Failed"
            else "skipped"
        )

        if truthy(is_recovery):
            update_table_session_result(
                audit_table_session_id=audit_table_session_id,
                status=audit_status,
                processed_rows=processed_rows,
            )
        else:
            append_table_session_result(
                audit_table_session_id=audit_table_session_id,
                table_id=table_id,
                load_type=load_type,
                status=audit_status,
                start_time=start_time,
                end_time=end_time,
                processed_rows=processed_rows,
            )
        if not is_success_status(status):
            append_error_log(
                audit_table_session_id,
                "DEPENDENCY_SKIPPED" if status == "Skipped" else "TRANSFORM_FAILED",
                error_message,
            )

        table_results.append({
            "table_id": to_int(table_id),
            "target_table": table_name,
            "status": status,
            "processed_rows": processed_rows,
            "audit_table_session_id": audit_table_session_id,
            "error": error_message if not is_success_status(status) else "",
            "exit_payload": payload,
        })

    final_status = "failed" if any(not is_success_status(item["status"]) for item in table_results) else "success"
    output = {"status": final_status, "tables": table_results}

    if not is_success_status(final_status) and truthy(fail_fast):
        raise RuntimeError(json.dumps(output, default=str))
    if runmultiple_failed is not None and not is_success_status(final_status):
        raise RuntimeError(json.dumps(output, default=str))

    exit_notebook(json.dumps(output, default=str))


run_parent()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
