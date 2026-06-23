# Define Load Type - Bronze Layer

## 1. Scope

Data is not loaded directly from source systems into Bronze. The ingestion flow is:

```text
Source System / Raw Extract
        |
        v
Landing Zone
        |
        v
Bronze Layer
```

This document defines the load type for the step:

```text
Landing Zone -> Bronze Layer
```

The source systems still matter because they define the original data structure, but Bronze should read from validated landing files/extracts.

| Source Group | Source System | Landing Data | Bronze Objects |
|---|---|---|---|
| CRM Source | SQL Server `insurance_crm_db` | SQL extracts landed by batch date | `customers`, `agents`, `insurance_providers`, `vehicle`, `quotation`, `quotation_item` |
| Policy Domain Source | JSON files | JSON files landed by batch date | `policy`, `payment`, `cancellation` |

Policy, payment, and cancellation are loaded only from JSON files. They are not loaded directly from SQL Server for this Bronze design. Bronze should create one table per policy-domain object and use the landed JSON files as the ingestion path, because the JSON files include `operation_type`, `last_updated`, `batch_date`, and `source_system`.

SQL Server ingestion applies only to the CRM source database `insurance_crm_db`.

Bronze stores raw structured data from Landing with ingestion metadata. Deduplication, merge, relationship validation, and applying final Insert/Update/Delete results are handled in Silver.

## 2. Layer Responsibility

| Layer | Responsibility | Example |
|---|---|---|
| Source System / Raw Extract | Original database tables or raw files. | CRM SQL Server tables, policy-domain JSON files. |
| Landing Zone | Immutable storage area for extracted files/data, partitioned by ETL date or batch date. | `/landing/crm/customers/etl_date=2026-05-25/`, `/landing/policy/policy/batch_date=2026-05-25/` |
| Bronze Layer | Raw structured tables loaded from Landing after technical checks. | `bronze_customers`, `bronze_policy`, `bronze_payment` |
| Silver Layer | Cleaned, deduplicated, validated, merged current-state data. | `silver_customers`, `silver_policy`, `silver_payment` |

## 3. Load Type Definitions

Only 2 load types are used for Landing -> Bronze:

| Load Type | Meaning | Landing -> Bronze Behavior | When To Use |
|---|---|---|---|
| `Full Load` | Load the full dataset available in Landing for the run. | Read the full landed extract/file set and append/store it as a Bronze batch snapshot. | Initial load, reference reload, full SQL extract, or source without reliable CDC/watermark. |
| `Incremental Load` | Load only new or changed records/events available in Landing for the run. | Read landed incremental files/events and append them to Bronze with batch/checkpoint metadata. | Source provides reliable watermark or CDC metadata such as `operation_type`, `last_updated`, and `batch_date`. |

## 4. Landing To Bronze Technical Checks

Before loading a landing batch into Bronze, the pipeline should use the metadata architecture tables to drive and track the load.

| Check Step | Metadata Table | What To Check | Applies To | Failed Action |
|---|---|---|---|---|
| Active configuration check | `cfg_landing_bronze_table` | Confirm the table has `is_active = 1` and has valid `source_system`, `source_schema`, `source_table`, `destination_schema`, `destination_table`, `primary_key_column`, and `load_type`. | All Landing -> Bronze loads | Do not run the table load; log failure. |
| Load type check | `cfg_landing_bronze_table` | Confirm `load_type` is only `full` or `incremental`. | All Landing -> Bronze loads | Stop load; invalid configuration. |
| Landing target check | `cfg_landing_bronze_table` | Confirm the configured Landing/Bronze destination exists and matches the object being loaded. | All Landing -> Bronze loads | Stop load; log configuration or path error. |
| ETL date check | Pipeline parameter + landing path | Confirm pipeline ETL date matches landing folder/file date, for example `etl_date=2026-05-25`. | SQL extracts and JSON files | Stop load or quarantine the file/batch. |
| Batch date check | Landing data + source field | Confirm source `batch_date` matches the landing partition/batch date. | JSON policy/payment/cancellation files | Stop load or quarantine records with wrong `batch_date`. |
| Schema check | `cfg_landing_bronze_table` + landing file/table | Confirm expected source columns exist and can be parsed into Bronze columns. | SQL extracts and JSON files | Stop load and write error to `audit_error_log`. |
| Primary key check | `cfg_landing_bronze_table.primary_key_column` | Confirm configured primary key column exists and is populated enough for downstream dedupe/merge. | All tables | Reject/quarantine bad records or fail table load based on rule. |
| Record count check | Landing file/table + `audit_table_session_log` | Count input rows and compare with expected non-empty rule. Store row metrics. | All tables | Warn or fail based on source rule. |
| Duplicate batch/session check | `audit_table_session_log` | Confirm the same `table_id` and ETL/batch run has not already succeeded. | All tables | Skip idempotently or stop duplicate load. |
| Watermark configuration check | `cfg_landing_bronze_table`, `cfg_table_watermark` | For incremental loads, confirm `source_watermark_column` exists and the table has previous `last_watermark_value` if applicable. | Incremental loads | Stop load or run initial incremental baseline rule. |
| Watermark value check | `cfg_table_watermark` | Load only records newer than `last_watermark_value`, for example `last_updated > last_watermark_value`. | Incremental loads | Quarantine out-of-order records or process by late-arriving rule. |
| CDC operation check | Landing JSON file | Confirm `operation_type` is valid: `I`, `U`, `D`. | JSON incremental files | Reject invalid CDC records and log to `audit_error_log`. |
| Audit session start | `audit_batch_log`, `audit_session_log`, `audit_table_session_log` | Create/update batch, session, and table session rows with status `Running`. | All loads | Stop if audit session cannot be created. |
| Audit session finish | `audit_table_session_log`, `audit_session_log`, `audit_batch_log` | Update status, start/end time, inserted/updated/deleted rows. | All loads | Mark failed if metrics cannot be written. |
| Error logging | `audit_error_log` | Store failed step name, error code, error message, and error time. | All failed loads | Required for failed load troubleshooting. |
| Watermark update | `cfg_table_watermark` | After successful incremental load, update `last_watermark_value`, `last_audit_session`, and `last_load_time`. | Incremental loads | Do not update watermark if table load failed. |

In this metadata design, the "check mark/checkpoint" concept is handled mainly by `cfg_table_watermark` and the audit log tables:

| Concept | Metadata Table | How It Is Used |
|---|---|---|
| Load configuration | `cfg_landing_bronze_table` | Defines which source object is loaded, target table, primary key, watermark column, and load type. |
| Watermark / checkpoint | `cfg_table_watermark` | Stores the last successfully processed watermark and last successful audit session. |
| Batch status | `audit_batch_log` | Tracks the overall master ETL batch. |
| Pipeline/session status | `audit_session_log` | Tracks each pipeline run. |
| Table-level status and row counts | `audit_table_session_log` | Tracks each table load, status, row counts, and timing. |
| Error details | `audit_error_log` | Stores technical errors for failed steps. |

## 5. CRM SQL Source - Landing To Bronze Load Type

SQL Server tables in `insurance_crm_db` do not have reliable `updated_at`, `operation_type`, or delete indicator columns. Therefore CRM SQL Server extracts should land first as full extracts, then Bronze loads them as `Full Load`.

| Source DB | Source Table | Landing Extract | Primary Key | Available Date / Watermark | Bronze Load Type | Reason |
|---|---|---|---|---|---|---|
| `insurance_crm_db` | `customers` | Full SQL extract landed by ETL date | `customer_id` | `created_date` | `Full Load` | `created_date` detects new customers only, not updates/deletes. |
| `insurance_crm_db` | `agents` | Full SQL extract landed by ETL date | `agent_id` | `created_date` | `Full Load` | Small master table. No reliable update/delete tracking. |
| `insurance_crm_db` | `insurance_providers` | Full SQL extract landed by ETL date | `provider_code` | None; has `active_flag` | `Full Load` | Small reference table. `active_flag` is business status, not CDC. |
| `insurance_crm_db` | `vehicle` | Full SQL extract landed by ETL date | `vehicle_id` | None | `Full Load` | No created/updated timestamp and no delete tracking. |
| `insurance_crm_db` | `quotation` | Full SQL extract landed by ETL date | `quotation_id` | `quotation_date`, `quotation_expiry_date` | `Full Load` | `quotation_status` can change, but table has no `updated_at`; incremental by `quotation_date` would miss updates. |
| `insurance_crm_db` | `quotation_item` | Full SQL extract landed by ETL date | `quotation_item_id` | None | `Full Load` | No reliable watermark or delete tracking. |

### CRM SQL Notes

- Landing should keep the raw SQL extract files/data by `etl_date`.
- Bronze should load the validated landing extract and add ingestion metadata.
- Silver can compare Bronze snapshots to detect changed/missing records.
- If source owner later enables SQL Server CDC, Change Tracking, or adds `updated_at` and `is_deleted`, the affected table can move from `Full Load` to `Incremental Load`.

## 6. Policy Domain JSON - Landing To Bronze Load Type

Policy-domain data is provided as JSON files and then landed by batch date. These objects are not loaded from SQL Server into Bronze.

| Metadata Column | Meaning |
|---|---|
| `last_updated` | Watermark timestamp |
| `operation_type` | CDC operation: `I = Insert`, `U = Update`, `D = Delete` |
| `batch_date` | Business/source batch date |
| `source_system` | Source system value provided inside the JSON file |

Because of that, policy-domain JSON uses both load types:

| Landing File Type | Bronze Load Type | Description |
|---|---|---|
| Full JSON files | `Full Load` | Initial baseline files. Current full files have `operation_type = I`. |
| Daily JSON files | `Incremental Load` | Daily Insert/Update/Delete events through `operation_type`. |

| JSON Object | Landing File Example | Primary Key | ETL/Checkpoint Check | Bronze Load Type |
|---|---|---|---|---|
| Policy | `policy_full_2026-05-25.json`; daily `policy_YYYY-MM-DD.json` | `policy_id` | Check `batch_date`, `last_updated`, checkpoint, and `operation_type` | `Full Load` for full file; `Incremental Load` for daily files |
| Payment | `payment_full_2026-05-25.json`; daily `payment_YYYY-MM-DD.json` | `payment_id` | Check `batch_date`, `last_updated`, checkpoint, and `operation_type` | `Full Load` for full file; `Incremental Load` for daily files |
| Cancellation | `cancellation_full_2026-05-25.json`; daily `cancellation_YYYY-MM-DD.json` | `cancellation_id` | Check `batch_date`, `last_updated`, checkpoint, and `operation_type` | `Full Load` for full file; `Incremental Load` for daily files |

### JSON Full Load

The full JSON files dated `2026-05-25` should be landed first, then loaded from Landing to Bronze as `Full Load`.

| Landing File | Record Count | Current `operation_type` | Bronze Load Type |
|---|---:|---|---|
| `policy_full_2026-05-25.json` | 600 | `I` | `Full Load` |
| `payment_full_2026-05-25.json` | 600 | `I` | `Full Load` |
| `cancellation_full_2026-05-25.json` | 60 | `I` | `Full Load` |

### JSON Incremental Load

Daily JSON files should be landed first, then loaded from Landing to Bronze as `Incremental Load`.

| Scenario | Example From Script | Expected `operation_type` | Landing -> Bronze Handling |
|---|---|---|---|
| Insert new policy | `POL900001` | `I` | Append raw insert event to Bronze after checkpoint/date validation |
| Update existing policy | `POL00100` status changed to `CANCELLED` | `U` | Append raw update event to Bronze after checkpoint/date validation |
| Delete policy | `POL00555` delete event in JSON incremental file | `D` | Append raw delete event to Bronze after checkpoint/date validation |
| Insert new payment | `PAY900001` | `I` | Append raw insert event to Bronze after checkpoint/date validation |
| Update existing payment | `PAY00200` status changed to `FAILED` | `U` | Append raw update event to Bronze after checkpoint/date validation |
| Insert new cancellation | `CAN900001` | `I` | Append raw insert event to Bronze after checkpoint/date validation |

## 7. Proposed Bronze Tables

| Bronze Table | Landing Source | Bronze Load Type |
|---|---|---|
| `bronze_customers` | Landing full extract from `insurance_crm_db.customers` | `Full Load` |
| `bronze_agents` | Landing full extract from `insurance_crm_db.agents` | `Full Load` |
| `bronze_insurance_providers` | Landing full extract from `insurance_crm_db.insurance_providers` | `Full Load` |
| `bronze_vehicle` | Landing full extract from `insurance_crm_db.vehicle` | `Full Load` |
| `bronze_quotation` | Landing full extract from `insurance_crm_db.quotation` | `Full Load` |
| `bronze_quotation_item` | Landing full extract from `insurance_crm_db.quotation_item` | `Full Load` |
| `bronze_policy` | Landing JSON files for policy | `Full Load` for baseline; `Incremental Load` for daily files |
| `bronze_payment` | Landing JSON files for payment | `Full Load` for baseline; `Incremental Load` for daily files |
| `bronze_cancellation` | Landing JSON files for cancellation | `Full Load` for baseline; `Incremental Load` for daily files |

## 8. Final Decision

| Source Group | Final Landing -> Bronze Load Type Decision |
|---|---|
| CRM Source | Only `insurance_crm_db` is extracted to Landing, then loaded to Bronze using `Full Load` because current SQL schema does not provide reliable update/delete CDC columns. |
| Policy Domain Source | Policy, payment, and cancellation are loaded only from JSON files stored in Landing. Bronze uses `Full Load` for initial full JSON files and `Incremental Load` for daily JSON files using `operation_type`, `last_updated`, `batch_date`, ETL date validation, and checkpoint/control table checks. |
