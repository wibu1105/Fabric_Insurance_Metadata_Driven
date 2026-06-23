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

audit_batch_id = ""
audit_session_id = ""
pipeline_name = "pl_silver_to_gold"
triggered_by = ""
target_tables = ""
rows = ""
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

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType, TimestampType

try:
    import com.microsoft.spark.fabric  # type: ignore # noqa: F401
    from com.microsoft.spark.fabric.Constants import Constants  # type: ignore
except Exception:
    Constants = None

spark = SparkSession.builder.getOrCreate()

TABLE_DEPENDENCIES = {
    "dimagent": [],
    "dimcustomer": [],
    "dimpaymenttype": [],
    "dimpolicyinfo": [],
    "dimprovider": [],
    "dimquotationinfo": [],

    "dimvehicle": ["dimcustomer"],
    
    "factcancellation": ["dimdate", "dimcustomer", "dimagent", "dimprovider", "dimpolicyinfo"],
    "factpayment": ["dimcustomer", "dimagent", "dimprovider", "dimdate", "dimpolicyinfo", "dimpaymenttype"],
    "factpolicy": ["dimdate", "dimcustomer", "dimprovider", "dimquotationinfo", "dimpolicyinfo", "dimagent"],
    "factquotationitem": ["dimdate", "dimprovider", "dimcustomer", "dimagent", "dimquotationinfo"]
}

DEPENDENCY_OVERRIDES = {
    "dimagent": 1,
    "dimcustomer": 1,
    "dimpaymenttype": 1,
    "dimpolicyinfo": 1,
    "dimprovider": 1,
    "dimvehicle": 2,
    "dimquotationinfo": 1,
    "factcancellation": 3,
    "factpayment": 3,
    "factpolicy": 3,
    "factquotationitem": 3,
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


def warehouse_table(table_name):
    if blank(audit_warehouse_name):
        raise ValueError("audit_warehouse_name is required when audit_sink = 'warehouse'")
    return f"{audit_warehouse_name}.audit.{table_name}"


def write_warehouse_table(df, table_name, mode="append"):
    writer = df.write.mode(mode)
    if Constants is not None:
        if not blank(audit_warehouse_workspace_id):
            writer = writer.option(Constants.WorkspaceId, audit_warehouse_workspace_id)
        if not blank(audit_warehouse_id):
            writer = writer.option(Constants.DatawarehouseId, audit_warehouse_id)
    writer.synapsesql(warehouse_table(table_name))


def append_table_session_result(audit_table_session_id, table_id, load_type, status, start_time, end_time, processed_rows=0):
    audit_df = spark.createDataFrame(
        [{
            "audit_table_session_id": audit_table_session_id,
            "audit_session_id": audit_session_id,
            "table_id": to_int(table_id),
            "layer_name": "gold",
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


def append_error_log(audit_table_session_id, error_code, error_message):
    safe_error = str(error_message).replace("|", " ").replace("\r", " ").replace("\n", " ")
    audit_df = spark.createDataFrame(
        [{
            "audit_error_id": str(uuid.uuid4()),
            "audit_table_session_id": audit_table_session_id,
            "step_name": "RUN GOLD RUNMULTIPLE PARENT",
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


def load_gold_config():
    selected_tables = {
        item.strip().lower()
        for item in str(target_tables or "").split(",")
        if item.strip()
    }

    input_rows = normalize_rows(rows)
    if input_rows is None:
        cfg_df = spark.table("cfg.cfg_silver_gold_table")
        cfg_columns = {field.name.lower() for field in cfg_df.schema.fields}
        is_active_expr = "is_active" if "is_active" in cfg_columns else "true AS is_active"
        input_rows = spark.sql(f"""
            SELECT
                table_id,
                layer_name,
                target_schema,
                target_table,
                primary_key_column,
                watermark_column,
                notebook_id,
                load_type,
                dependency_level,
                {is_active_expr}
            FROM cfg.cfg_silver_gold_table
            WHERE lower(layer_name) = 'gold'
        """).collect()

    configs = []
    seen_tables = set()
    for row in input_rows:
        item = row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        table_name = str(item["target_table"]).lower()
        if table_name not in TABLE_DEPENDENCIES:
            print(f"Skipping unsupported gold table: {table_name}")
            continue
        if selected_tables and table_name not in selected_tables:
            continue
        if table_name in seen_tables:
            print(f"Skipping duplicate gold table config: {table_name}")
            continue
        if not truthy(item.get("is_active", True)):
            continue
        if truthy(force_dependency_overrides):
            item["dependency_level"] = DEPENDENCY_OVERRIDES.get(table_name, to_int(item.get("dependency_level"), 99))
        item["target_table"] = table_name
        item["target_schema"] = item.get("target_schema", "gold") or "gold"
        item["audit_table_session_id"] = str(uuid.uuid4())
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
                "target_schema": str(cfg.get("target_schema", "gold")),
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

    if blank(audit_session_id):
        audit_session_id = str(uuid.uuid4())
    if blank(audit_batch_id):
        audit_batch_id = audit_session_id
    if truthy(manage_session_audit):
        raise ValueError("manage_session_audit must be false. Use pipeline Script activities for session start/end.")

    configs = load_gold_config()
    if not configs:
        exit_notebook(json.dumps({"status": "success", "message": "No active gold tables"}, default=str))

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
                status = payload.get("status", "success")
                processed_rows = to_int(payload.get("processed_rows", 0))
                start_time = parse_ts(payload.get("start_time"), parent_start)
                end_time = parse_ts(payload.get("end_time"), now_after_run)
                error_message = payload.get("error", "")

        append_table_session_result(
            audit_table_session_id=audit_table_session_id,
            table_id=table_id,
            load_type=load_type,
            status=status.lower(),
            start_time=start_time,
            end_time=end_time,
            processed_rows=processed_rows,
        )
        if status != "success":
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
            "error": error_message if status != "success" else "",
            "exit_payload": payload,
        })

    final_status = "Failed" if any(item["status"] != "success" for item in table_results) else "success"
    output = {"status": final_status, "tables": table_results}

    if final_status != "success" and truthy(fail_fast):
        raise RuntimeError(json.dumps(output, default=str))
    if runmultiple_failed is not None and final_status != "success":
        raise RuntimeError(json.dumps(output, default=str))

    exit_notebook(json.dumps(output, default=str))


run_parent()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
