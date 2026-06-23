# 🔁 Recovery Pipeline — Metadata-Driven Auto Recovery

> **Objective:** When an ETL pipeline fails mid-run, the system automatically detects which layer failed, retrieves the list of tables to re-run from audit metadata, and reprocesses **only the failed portion** — without restarting the entire batch.

---

## 📐 Recovery Flow Diagram

![Recovery Pipeline Flow](images/recovery_flow_diagram.png)

---

## 🧠 Design Philosophy: Metadata-Driven Recovery

Recovery contains no hardcoded logic. All decisions are read from **audit tables** stored in the Warehouse:

```
Questions the system answers automatically:
  1. Which batch failed most recently?   → audit.audit_batch_log
  2. Which layer failed?                 → audit.audit_table_session_log (layer_name)
  3. Which specific tables failed?       → audit.audit_table_session_log (status <> 'success')
  4. Which notebook should be re-run?    → cfg.cfg_silver_gold_table (notebook_id)
  5. What is the dependency order?       → cfg.cfg_silver_gold_table (dependency_level)
```

**Nothing is hardcoded in the pipelines** — when a new table is added to the metadata config, recovery automatically includes it.

---

## 📋 Recovery Pipeline Components

### Pipelines & Notebooks

| Artifact | Type | Role |
|---|---|---|
| `pl_recovery_table_session` | Pipeline | **Main orchestrator** — coordinates the entire recovery process |
| `pl_recovery_source_to_landing` | Pipeline | Re-ingests data from source to Landing layer |
| `pl_recovery_landing_to_bronze` | Pipeline | Re-runs Landing → Bronze |
| `pl_recovery_bronze_to_silver` | Pipeline | Re-runs Bronze → Silver |
| `pl_recovery_silver_to_gold` | Pipeline | Re-runs Silver → Gold |
| `nb_define_failed_layer` | Notebook | Identifies the failed layer from audit logs |
| `nb_get_failed_session_table` | Notebook | Retrieves the list of failed tables as JSON |
| `nb_copy_data_to_bronze` | Notebook | Re-executes the copy logic back to Bronze |
| `nb_gold_parent_recovery` | Notebook | Orchestrates the Gold DAG re-run (SCD + Fact) |
| `nb_update_status` | Notebook | Updates audit log status after recovery completes |

---

## 🔄 Step-by-Step Recovery Flow

### Step 1: Trigger `pl_recovery_table_session`

This pipeline is triggered manually or automatically after a batch failure. It accepts 3 parameters:

```json
{
  "p_triggered_by": "system",
  "p_batch_date": "2026-06-23",
  "p_batch_date_source": "2026-05-25"
}
```

---

### Step 2: `Get_Recovery_Layer` — Query metadata to identify the failed batch

The pipeline runs a SQL Script activity directly on **Rookie2Engineer_Warehouse**:

```sql
SELECT DISTINCT
    COALESCE(MAX(abl.audit_batch_id), 'DEFAULT') AS audit_batch_id,
    COALESCE(MAX(atsl.layer_name), 'DEFAULT')    AS layer_name
FROM audit.audit_table_session_log atsl
JOIN audit.audit_session_log asl
    ON atsl.audit_session_id = asl.audit_session_id
JOIN audit.audit_batch_log abl
    ON abl.audit_batch_id = asl.audit_batch_id
WHERE abl.audit_batch_id = (
    SELECT TOP 1 audit_batch_id
    FROM audit.audit_batch_log
    ORDER BY session_start DESC   -- fetch the MOST RECENT batch
)
  AND lower(atsl.status) <> 'success'  -- only tables that failed
```

**Output:** `audit_batch_id` + `layer_name` of the most recently failed batch.

---

### Step 3: `Set v_audit_batch_id` — Store batch_id in a pipeline variable

```
v_audit_batch_id = @activity('Get_Recovery_Layer').output.resultSets[0].rows[0].audit_batch_id
```

This variable is passed to all recovery sub-pipelines so they know which batch to reprocess.

---

### Step 4: `Choose Recovery Case` — Switch by failed layer

The pipeline uses a **Switch activity** to route to the correct recovery pipeline:

```
layer_name = "landing"  →  pl_recovery_source_to_landing → pl_recovery_landing_to_bronze
layer_name = "bronze"   →  pl_recovery_landing_to_bronze
layer_name = "silver"   →  pl_recovery_bronze_to_silver
layer_name = "gold"     →  pl_recovery_silver_to_gold
DEFAULT (no failure)    →  pl_etl_master_optimize (triggers a full new batch)
```

> **Why does "landing" trigger two steps?**  
> If Landing fails, Bronze has no data yet — data must be re-ingested from source before Bronze can run.

---

### Step 5: Inside Each Recovery Sub-pipeline

Every `pl_recovery_*` pipeline executes 4 sequential steps:

#### 5.1 — `nb_define_failed_layer`: Identify the failed layer

```python
# Input parameter: p_audit_batch_id
query = f"""
SELECT DISTINCT atsl.layer_name
FROM audit.audit_table_session_log atsl
JOIN audit.audit_session_log asl ON atsl.audit_session_id = asl.audit_session_id
JOIN audit.audit_batch_log abl ON abl.audit_batch_id = asl.audit_batch_id
WHERE abl.audit_batch_id = '{p_audit_batch_id}'
  AND lower(atsl.status) <> 'success'
"""
layer = df.first()["layer_name"]
mssparkutils.notebook.exit(layer)  # returns "gold" / "silver" / "bronze"
```

#### 5.2 — `nb_get_failed_session_table`: Retrieve the list of failed tables

```python
# Input parameters: p_audit_batch_id, layer_name
query = f"""
SELECT
    atsl.audit_session_id,
    atsl.audit_table_session_id,
    csgt.notebook_id,           -- notebook to re-run
    csgt.target_schema,
    csgt.target_table,
    csgt.table_id,
    csgt.dependency_level       -- used to determine execution order
FROM audit.audit_table_session_log atsl
JOIN cfg.cfg_silver_gold_table csgt ON csgt.table_id = atsl.table_id
WHERE abl.audit_batch_id = '{p_audit_batch_id}'
  AND lower(atsl.status) <> 'success'
  AND atsl.layer_name = '{layer_name}'
"""
# Returns a JSON list:
# [{"audit_table_session_id": "...", "notebook_id": "...", "target_table": "...", "dependency_level": 1}, ...]
mssparkutils.notebook.exit(json.dumps(result))
```

> **This is the key connection to Metadata:**  
> `cfg.cfg_silver_gold_table` provides the `notebook_id` and `dependency_level` for each table.  
> Recovery uses this information to determine **which notebook to run** and **in what order**.

#### 5.3 — Re-run notebooks following dependency order

Based on the JSON from the previous step, the pipeline or `nb_gold_parent_recovery` will:
1. Group tables by `dependency_level`
2. Run tables at the same level in parallel (DAG via `runMultiple`)
3. Proceed to the next level only after the previous level completes

```python
# nb_gold_parent_recovery — build DAG from failed tables
dag = build_dag(configs)            # sorted by dependency_level
utils.notebook.validateDAG(dag)
raw_results = utils.notebook.runMultiple(dag, {"displayDAGViaGraphviz": False})
```

#### 5.4 — `nb_update_status`: Update audit log

```python
# Update audit_session_log
UPDATE audit.audit_session_log
SET session_status = '{session_status}',
    session_end = CASE
        WHEN '{session_status}' IN ('success', 'failed') THEN current_timestamp()
        ELSE NULL
    END
WHERE audit_session_id = '{audit_session_id}'

# Update audit_table_session_log
UPDATE audit.audit_table_session_log
SET status = '{table_status}',
    end_time = CASE
        WHEN '{table_status}' IN ('success', 'failed') THEN current_timestamp()
        ELSE NULL
    END,
    updated_at = current_timestamp()
WHERE audit_table_session_id = '{audit_table_session_id}'
```

---

### Step 6: Update `audit_batch_log` — Close out the recovery run

After the recovery sub-pipeline completes (success or failure), the orchestrator calls a Stored Procedure:

```sql
-- On success:
EXEC [audit].[sp_audit_batch_log] @action = 'success', @audit_batch_id = '{v_audit_batch_id}'

-- On failure:
EXEC [audit].[sp_audit_batch_log] @action = 'failed',  @audit_batch_id = '{v_audit_batch_id}'
```

---

## 🗄️ Metadata Tables Involved in Recovery

### `audit.audit_batch_log`
```
audit_batch_id  │ session_start        │ batch_status
─────────────────┼──────────────────────┼─────────────
batch-001        │ 2026-06-23 09:00:00  │ failed       ← Recovery will process this batch
batch-000        │ 2026-06-22 09:00:00  │ success
```

### `audit.audit_session_log`
```
audit_session_id │ audit_batch_id │ session_status │ layer_name
──────────────────┼────────────────┼────────────────┼────────────
session-A         │ batch-001      │ failed         │ gold
session-B         │ batch-001      │ success        │ silver
```

### `audit.audit_table_session_log`
```
audit_table_session_id │ audit_session_id │ table_id │ layer_name │ status
────────────────────────┼──────────────────┼──────────┼────────────┼────────
ts-001                  │ session-A        │ 5        │ gold       │ failed   ← needs re-run
ts-002                  │ session-A        │ 6        │ gold       │ success
```
→ Recovery identifies that `table_id = 5` in the `gold` layer needs to be re-processed.

### `cfg.cfg_silver_gold_table`
```
table_id │ target_table       │ notebook_id   │ dependency_level │ is_active
──────────┼────────────────────┼───────────────┼──────────────────┼──────────
5         │ fact_policy        │ nb-gold-fact  │ 2                │ 1
6         │ dim_customer       │ nb-gold-dim   │ 1                │ 1
```
→ Recovery uses `notebook_id = nb-gold-fact` and runs it after `dependency_level = 1` completes.

---

## 💡 Summary: Fully Metadata-Driven Recovery

```
Nothing is hardcoded in the recovery pipelines.

When a new Gold table is added to cfg.cfg_silver_gold_table:
  → Recovery automatically knows which notebook to run
  → Execution order is determined by dependency_level
  → Audit log is updated automatically upon completion

When a batch fails at any layer:
  → Simply trigger pl_recovery_table_session
  → The system detects the most recent failed batch
  → Identifies the failed layer and specific tables
  → Reruns only those tables and updates audit status
```

---

## 📁 Source Files

| File | Path |
|---|---|
| Orchestrator Pipeline | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/pl_recovery_table_session.DataPipeline/` |
| Bronze Recovery Pipeline | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/pl_recovery_landing_to_bronze.DataPipeline/` |
| Silver Recovery Pipeline | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/pl_recovery_bronze_to_silver.DataPipeline/` |
| Gold Recovery Pipeline | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/pl_recovery_silver_to_gold.DataPipeline/` |
| Define Failed Layer NB | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/nb_define_failed_layer.Notebook/` |
| Get Failed Tables NB | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/nb_get_failed_session_table.Notebook/` |
| Update Status NB | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/nb_update_status.Notebook/` |
| Gold Parent Recovery NB | `Rookie2Engineer/fabric_source/recovery_pipeline_folder/nb_gold_parent_recovery.Notebook/` |

---

*Part of the [Rookie2Engineer](../README.md) — Fabric Insurance Metadata-Driven Platform*
