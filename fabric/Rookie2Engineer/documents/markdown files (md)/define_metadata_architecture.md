# Metadata Architecture Documentation

![metadata_architecture](/Rookie2Engineer/documents/images/metadata_architecture.png)
<p align="center">
  <em>Metadata Architecture ERD</em>
</p>

## 1. Introduction
The Metadata Architecture serves as the governance foundation for the ETL (Extract, Transform, Load) system. It enables automation, orchestration, and monitoring of data processing across all layers (Landing, Bronze, Silver, and Gold). The architecture is divided into two primary functional groups: **Configuration Metadata** (defining processing behavior) and **Audit & Log Metadata** (tracking operational status).

---

## 2. Configuration Metadata
This group stores the parameters required to drive ETL pipelines, including source-to-target mappings and loading strategies.

### 2.1. Landing & Bronze Configuration (`cfg_landing_bronze_table`)
Manages the ingestion of data from source systems into the Landing and Bronze layers.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `table_id` | integer | Unique identifier for the configuration record. | 105 |
| `source_system` | varchar | Originating system name. | SQLServer_CRM |
| `source_schema`| varchar | Schema name of the source table in the source system. | dbo |
| `source_table`| varchar | Name of the source table to be ingested. | customer |
| `source_watermark_column`| varchar | Column used to identify new/updated records. | null |
| `destination_system` | varchar | Target system used for storing data. | Lakehouse |
| `destination_schema` | varchar | Schema name of the target table. | landing |
| `destination_table` | varchar | Table name where data is loaded. | customer |
| `primary_key_column`| varchar | Column used for deduplication, merge, or upsert. | id |
| `load_type` | varchar | Strategy type (full or incremental load). | full |
| `is_active` | bit | Indicates whether the configuration is active and eligible for execution. | 1 |
| `created_date` | datetime | Date and time when the configuration record was created. | 2025-05-25 10:39:10 |
| `updated_date` | datetime | Date and time when the configuration record was last updated. | 2027-05-25 13:19:50 |

### 2.2. Silver & Gold Configuration (`cfg_silver_gold_table`)
Defines the transformation and orchestration logic for the Silver and Gold layers.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `table_id` | integer | Unique identifier of each configured table. | 1005 |
| `layer_name` | varchar | Data layer (silver, gold). | gold |
| `target_schema` | varchar | Target schema name in Lakehouse. | gold |
| `target_table` | varchar | Target table name in Lakehouse. | fact_payment |
| `primary_key_column` | varchar | Primary key column used for deduplication or merge operations. | payment_id |
| `watermark_column` | varchar | Column used for incremental loading and change tracking. | last_updated |
| `notebook_id` | varchar | Unique identifier or path of the notebook responsible for processing the table. | c29c9fbe-9ca1-40ae-bf31-c6d94cab4f11 |
| `load_type` | varchar | Data loading strategy for the table. | incremental |
| `dependency_level` | integer | Execution priority level used for orchestration dependency. | 2 |
| `is_active` | bit | Indicates whether the configuration is active and eligible for execution. | 1 |
| `created_date` | datetime | Timestamp when the configuration record was created. | 2025-05-25 10:39:10 |
| `updated_date` | datetime | Timestamp when the configuration record was last updated. | 2027-05-25 13:19:50 |

### 2.3. Watermark Configuration (`cfg_table_watermark`)
Tracks the state of incremental loads to ensure data consistency and change tracking.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `table_id` | integer | Foreign key linked to configuration records. | 105 |
| `last_watermark_value`| datetime | The latest successfully processed watermark value. | 2026-05-25 10:00:00 |
| `last_audit_session` | varchar | The last successful execution session ID. | 40e4ef07-a67e-478e-95af-31ba16ac9134 |
| `last_load_time` | datetime | Timestamp of the last successful data load. |  2026-05-25 10:15:30 |
| `created_date` | datetime | Date and time when the watermark record was created. | 2025-05-25 10:39:30 |
| `updated_date` | datetime | Date and time when the watermark record was last updated. | 2026-05-25 10:15:30 |

---

## 3. Audit & Log Metadata
This group captures execution history, performance metrics, and exception details for pipeline monitoring.

### 3.1. Batch Log (`audit_batch_log`)
Records high-level master pipeline execution batches.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `audit_batch_id` | varchar | Unique ID for the master pipeline batch. | ccdbc1d9-c729-4be3-9827-d40af3374e8c |
| `batch_name` | varchar | Name of the master pipeline batch process. | 00_Master_ETL |
| `triggered_by` | varchar | User or process that triggered the batch execution. | admin |
| `batch_status` | varchar | Status (Started, Running, Succeeded, Failed). | Succeeded |
| `session_start` | datetime | Timestamp when the batch session started. | 2026-05-07 15:45:17 |
| `session_end` | datetime | Timestamp when the batch session completed. | 2026-05-07 17:12:34 |

### 3.2. Session Log (`audit_session_log`)
Captures detailed execution information for individual pipeline runs.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `audit_session_id` | varchar | Unique ID for the execution session. | 1057e459-838e-44a8-aac6-35f877d1d2ee |
| `audit_batch_id` | varchar | Unique ID for the master pipeline batch. | ccdbc1d9-c729-4be3-9827-d40af3374e8c |
| `pipeline_name` | varchar | Name of the executed pipeline. | bronze_to_silver_pipeline |
| `triggered_by` | varchar | User or process that triggered the pipeline execution. | admin |
| `session_status` | varchar | Status of the session (Started, Running, Succeeded, Failed). | Succeeded |
| `session_start` | datetime | Timestamp when the pipeline session started. | 2026-05-07 15:50:17 |
| `session_end` | datetime | Timestamp when the pipeline session completed. | 2026-05-07 15:55:34 |

### 3.3. Table Session Log (`audit_table_session_log`)
Logs processing details and performance metrics for each table within a session.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `audit_table_session_id`| varchar | Unique ID for the table execution session. | 6db7620e-c9e8-484a-ac9e-608adf1256a7 |
| `audit_session_id` | varchar | Unique identifier of the parent pipeline execution session. | 1057e459-838e-44a8-aac6-35f877d1d2ee |
| `table_id` | integer | Identifier of the configured table from configuration metadata table. | 105 |
| `layer_name` | varchar | Data layer where the table is processed. | bronze |
| `load_type` | varchar | Data loading strategy used during execution. | incremental |
| `status` | varchar | Processing status (Started, Running, Succeeded, Failed). | Succeeded |
| `start_time` | datetime | Timestamp when table processing started. | 2026-05-07 16:15:17 |
| `end_time` | datetime | Timestamp when table processing completed. | 2026-05-07 16:20:34 |
| `processed_rows`| integer | Number of rows successfully processed during pipeline execution. | 100 |
| `created_at`| datetime | Timestamp when the audit record was created. | 2026-05-07 16:15:17 |
| `updated_at`| datetime | Timestamp when the audit record was last updated. | 2026-05-07 16:20:34 |

### 3.4. Error Log (`audit_error_log`)
Stores detailed exception information to facilitate troubleshooting.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `audit_error_id` | varchar | Unique ID for the error record. | bf4fca49-c3ee-4186-9ed3-2bd111d66ea9 |
| `audit_table_session_id`| varchar | Identifier of the related table execution session. | 6db7620e-c9e8-484a-ac9e-608adf1256a7 |
| `step_name` | varchar | Processing step where the failure occurred. | COPY_DATA |
| `error_code` | varchar | System or application error code associated with the failure. | COPY_ERROR |
| `error_name` | varchar(max) | Detailed error message and exception trace. | Failure happened on 'Source' side. ErrorCode=UserErrorWriteFailedFileOperation,'Type=Microsoft.DataTransfer.Common.Shared.HybridDeliveryException,Message=The file operation is failed, upload file failed at path: '52ea5712-2efc-4774-91de-c52e979e54e4/9a57af0a-74d7-409f-b1d8-5bb5834bedd3/Staging/73686fe2-a74d-4c75-9316-47617582bf9e/MSSQLImportCommand/data_73686fe2-a74d-4c75-9316-47617582bf9e_ae407faf-1e21-405b-a441-a611b5e21ac1.parquet'.,Source=Microsoft.DataTransfer.Common,''Type=Microsoft.Data.SqlClient.SqlException,Message=Conversion failed when converting date and/or time from character string.,Source=Framework Microsoft SqlClient Data Provider,' |
| `error_time` | datetime | Timestamp when the error occurred. | 2026-05-07 15:46:20 |

### 3.5. Invalid Record Log (`audit_invalid_record`)

Stores records that fail validation rules during data cleansing and transformation processes. This table enables data quality monitoring, root cause analysis, and reprocessing of rejected records.

| Column | Data Type | Description | Data Sample |
| :--- | :--- | :--- | :--- |
| `invalid_record_id` | varchar | Unique identifier for the invalid record log entry. | 3ec0f31a-417e-49db-bb9d-92eae131848f |
| `audit_table_session_id` | varchar | Identifier of the related table execution session. | 6db7620e-c9e8-484a-ac9e-608adf1256a7 |
| `layer_name` | varchar | Data layer where the validation failure occurred. | Silver |
| `table_name` | varchar | Name of the table being processed. | customer |
| `invalid_column` | varchar | Column that failed the validation rule. | email |
| `invalid_reason` | varchar | Reason why the records were rejected. | Invalid email format |
| `invalid_record_count` | integer | Number of records rejected for the same validation rule and column. | 3 |
| `record_payload` | varchar(max) | JSON array containing the original rejected records for investigation, recovery, and reprocessing purposes. | `[{"customer_id":1001,"email":"abc.com","age":15},{"customer_id":1003,"email":"xyz.com","age":17},{"customer_id":1005,"email":"b.com","age":10}]` |
| `rejected_timestamp` | datetime | Timestamp when the records were rejected. | 2026-05-07 15:46:20 |
---
