# Bronze Table Definitions

## 1. Source Grouping Decision

Policy, payment, and cancellation are JSON-only sources for Bronze. They should not be loaded from SQL Server in this design.

For Bronze design, create one Bronze table per JSON business object:

| Business Object | Physical Source | Bronze Ingestion Path | Bronze Table |
|---|---|---|---|
| Policy | JSON files: `policy_full_*.json`, daily policy JSON files | Landing JSON full/incremental files | `policy` |
| Payment | JSON files: `payment_full_*.json`, daily payment JSON files | Landing JSON full/incremental files | `payment` |
| Cancellation | JSON files: `cancellation_full_*.json`, daily cancellation JSON files | Landing JSON full/incremental files | `cancellation` |

Reason: JSON files already include change event metadata: `operation_type`, `last_updated`, `batch_date`, and `source_system`. These columns are required to process Insert, Update, and Delete scenarios.

No database CDC is enabled or assumed for this Bronze design. The JSON `operation_type` column is treated as source-provided change event information, not SQL Server CDC.

CRM data is the only SQL Server source:

| Business Object | Source DB | Bronze Ingestion Path | Bronze Table |
|---|---|---|---|
| Customer | `insurance_crm_db` | Landing full SQL extract | `customers` |
| Agent | `insurance_crm_db` | Landing full SQL extract | `agents` |
| Insurance Provider | `insurance_crm_db` | Landing full SQL extract | `insurance_providers` |
| Vehicle | `insurance_crm_db` | Landing full SQL extract | `vehicle` |
| Quotation | `insurance_crm_db` | Landing full SQL extract | `quotation` |
| Quotation Item | `insurance_crm_db` | Landing full SQL extract | `quotation_item` |


## 2. Bronze Table Summary

| Bronze Table | Source Group | Source DB | Source Object | Load Type |
|---|---|---|---|---|
| `customers` | CRM Source | `insurance_crm_db` | `customers` | `Full Load` |
| `agents` | CRM Source | `insurance_crm_db` | `agents` | `Full Load` |
| `insurance_providers` | CRM Source | `insurance_crm_db` | `insurance_providers` | `Full Load` |
| `vehicle` | CRM Source | `insurance_crm_db` | `vehicle` | `Full Load` |
| `quotation` | CRM Source | `insurance_crm_db` | `quotation` | `Full Load` |
| `quotation_item` | CRM Source | `insurance_crm_db` | `quotation_item` | `Full Load` |
| `policy` | Policy Domain Source | `N/A - JSON file` | Policy JSON files | `Full Load` for baseline; `Incremental Load` for daily files |
| `payment` | Policy Domain Source | `N/A - JSON file` | Payment JSON files | `Full Load` for baseline; `Incremental Load` for daily files |
| `cancellation` | Policy Domain Source | `N/A - JSON file` | Cancellation JSON files | `Full Load` for baseline; `Incremental Load` for daily files |

## 3. Column Definition Template

Each Bronze table below uses the same column-level definition format.

| Column | Meaning |
|---|---|
| Source Group | Logical source group: `CRM Source` or `Policy Domain Source`. |
| Source DB | Source database name. Use `N/A - JSON file` for JSON-only policy-domain sources. |
| Source Object | Source table or JSON file/business object. |
| Source Column | Original source column name. |
| Bronze Table | Target Bronze table name. |
| Bronze Column | Target Bronze column name. |
| Source Data Type | Data type in source system or JSON file. |
| Bronze Data Type | Source-compatible Bronze data type. Bronze should keep raw/source data types as much as possible; business standardization happens in Silver. |
| Is Primary Key | Whether the column is a source/business primary key. |
| Reference Table / Column | Target reference table/column. Use `N/A` when the column does not reference another table. |
| Nullable | Whether the source column allows null or can be missing. |
| Default Value | Default value if applicable. |
| PII / Sensitive Flag | Whether the column contains PII or sensitive data. |
| Partition Column | Whether this column is used for partitioning. |
| Load Type | Bronze load type for the table. |
| Description | Business description. |

## 4. `customers`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `customers` | `customer_id` | `customers` | `customer_id` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique customer identifier. |
| CRM Source | `insurance_crm_db` | `customers` | `full_name` | `customers` | `full_name` | `NVARCHAR(200)` | string | No | N/A | No | N/A | PII | No | `Full Load` | Customer full name. |
| CRM Source | `insurance_crm_db` | `customers` | `gender` | `customers` | `gender` | `VARCHAR(10)` | string | No | N/A | Yes | N/A | Sensitive | No | `Full Load` | Customer gender. |
| CRM Source | `insurance_crm_db` | `customers` | `dob` | `customers` | `dob` | `DATE` | date | No | N/A | No | N/A | PII | No | `Full Load` | Date of birth. |
| CRM Source | `insurance_crm_db` | `customers` | `phone_number` | `customers` | `phone_number` | `VARCHAR(20)` | string | No | N/A | Yes | N/A | PII | No | `Full Load` | Customer phone number. |
| CRM Source | `insurance_crm_db` | `customers` | `email` | `customers` | `email` | `VARCHAR(200)` | string | No | N/A | Yes | N/A | PII | No | `Full Load` | Customer email. |
| CRM Source | `insurance_crm_db` | `customers` | `city` | `customers` | `city` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Customer city. |
| CRM Source | `insurance_crm_db` | `customers` | `district` | `customers` | `district` | `NVARCHAR(100)` | string | No | N/A | Yes | N/A | No | No | `Full Load` | Customer district. |
| CRM Source | `insurance_crm_db` | `customers` | `created_date` | `customers` | `created_date` | `DATETIME` | timestamp | No | N/A | No | Source/system generated value | No | No | `Full Load` | Customer creation timestamp. |

## 5. `agents`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `agents` | `agent_id` | `agents` | `agent_id` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique agent identifier. |
| CRM Source | `insurance_crm_db` | `agents` | `agent_name` | `agents` | `agent_name` | `NVARCHAR(200)` | string | No | N/A | No | N/A | PII | No | `Full Load` | Agent name. |
| CRM Source | `insurance_crm_db` | `agents` | `region` | `agents` | `region` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Sales region. |
| CRM Source | `insurance_crm_db` | `agents` | `branch` | `agents` | `branch` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Branch. |
| CRM Source | `insurance_crm_db` | `agents` | `manager_name` | `agents` | `manager_name` | `NVARCHAR(200)` | string | No | N/A | Yes | N/A | PII | No | `Full Load` | Manager name. |
| CRM Source | `insurance_crm_db` | `agents` | `created_date` | `agents` | `created_date` | `DATETIME` | timestamp | No | N/A | No | Source/system generated value | No | No | `Full Load` | Agent creation timestamp. |

## 6. `insurance_providers`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `insurance_providers` | `provider_code` | `insurance_providers` | `provider_code` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique insurance provider code. |
| CRM Source | `insurance_crm_db` | `insurance_providers` | `provider_name` | `insurance_providers` | `provider_name` | `NVARCHAR(200)` | string | No | N/A | No | N/A | No | No | `Full Load` | Provider name. |
| CRM Source | `insurance_crm_db` | `insurance_providers` | `provider_group` | `insurance_providers` | `provider_group` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Provider group. |
| CRM Source | `insurance_crm_db` | `insurance_providers` | `active_flag` | `insurance_providers` | `active_flag` | `INT` | int | No | N/A | No | N/A | No | No | `Full Load` | Active/inactive flag, not change tracking. |

## 7. `vehicle`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `vehicle` | `vehicle_id` | `vehicle` | `vehicle_id` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique vehicle identifier. |
| CRM Source | `insurance_crm_db` | `vehicle` | `customer_id` | `vehicle` | `customer_id` | `VARCHAR(20)` | string | No | `customers.customer_id` | Yes | N/A | No | No | `Full Load` | Owner customer identifier. |
| CRM Source | `insurance_crm_db` | `vehicle` | `plate_number` | `vehicle` | `plate_number` | `VARCHAR(20)` | string | No | N/A | Yes | N/A | Sensitive | No | `Full Load` | Vehicle plate number. |
| CRM Source | `insurance_crm_db` | `vehicle` | `vehicle_brand` | `vehicle` | `vehicle_brand` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Vehicle brand. |
| CRM Source | `insurance_crm_db` | `vehicle` | `vehicle_model` | `vehicle` | `vehicle_model` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Vehicle model. |
| CRM Source | `insurance_crm_db` | `vehicle` | `manufacture_year` | `vehicle` | `manufacture_year` | `INT` | int | No | N/A | Yes | N/A | No | No | `Full Load` | Manufacture year. |
| CRM Source | `insurance_crm_db` | `vehicle` | `vehicle_value` | `vehicle` | `vehicle_value` | `DECIMAL(18,2)` | decimal(18,2) | No | N/A | Yes | N/A | No | No | `Full Load` | Vehicle insured value. |

## 8. `quotation`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `quotation` | `quotation_id` | `quotation` | `quotation_id` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique quotation identifier. |
| CRM Source | `insurance_crm_db` | `quotation` | `customer_id` | `quotation` | `customer_id` | `VARCHAR(20)` | string | No | `customers.customer_id` | No | N/A | No | No | `Full Load` | Customer who requested the quotation. |
| CRM Source | `insurance_crm_db` | `quotation` | `agent_id` | `quotation` | `agent_id` | `VARCHAR(20)` | string | No | `agents.agent_id` | Yes | N/A | No | No | `Full Load` | Agent handling the quotation. |
| CRM Source | `insurance_crm_db` | `quotation` | `provider_code` | `quotation` | `provider_code` | `VARCHAR(20)` | string | No | `insurance_providers.provider_code` | Yes | N/A | No | No | `Full Load` | Provider quoted. |
| CRM Source | `insurance_crm_db` | `quotation` | `quotation_date` | `quotation` | `quotation_date` | `DATETIME` | timestamp | No | N/A | No | N/A | No | No | `Full Load` | Quotation creation date. |
| CRM Source | `insurance_crm_db` | `quotation` | `quotation_status` | `quotation` | `quotation_status` | `VARCHAR(50)` | string | No | N/A | No | N/A | No | No | `Full Load` | Quotation status. |
| CRM Source | `insurance_crm_db` | `quotation` | `package_code` | `quotation` | `package_code` | `VARCHAR(50)` | string | No | N/A | No | N/A | No | No | `Full Load` | Insurance package code. |
| CRM Source | `insurance_crm_db` | `quotation` | `premium_amount` | `quotation` | `premium_amount` | `DECIMAL(18,2)` | decimal(18,2) | No | N/A | No | N/A | No | No | `Full Load` | Quoted premium amount. |
| CRM Source | `insurance_crm_db` | `quotation` | `quotation_expiry_date` | `quotation` | `quotation_expiry_date` | `DATETIME` | timestamp | No | N/A | No | N/A | No | No | `Full Load` | Quotation expiry timestamp. |

## 9. `quotation_item`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CRM Source | `insurance_crm_db` | `quotation_item` | `quotation_item_id` | `quotation_item` | `quotation_item_id` | `VARCHAR(20)` | string | Yes | N/A | No | N/A | No | No | `Full Load` | Unique quotation item identifier. |
| CRM Source | `insurance_crm_db` | `quotation_item` | `quotation_id` | `quotation_item` | `quotation_id` | `VARCHAR(20)` | string | No | `quotation.quotation_id` | No | N/A | No | No | `Full Load` | Parent quotation identifier. |
| CRM Source | `insurance_crm_db` | `quotation_item` | `coverage_type` | `quotation_item` | `coverage_type` | `NVARCHAR(100)` | string | No | N/A | No | N/A | No | No | `Full Load` | Coverage type. |
| CRM Source | `insurance_crm_db` | `quotation_item` | `coverage_amount` | `quotation_item` | `coverage_amount` | `DECIMAL(18,2)` | decimal(18,2) | No | N/A | No | N/A | No | No | `Full Load` | Coverage amount. |
| CRM Source | `insurance_crm_db` | `quotation_item` | `deductible_amount` | `quotation_item` | `deductible_amount` | `DECIMAL(18,2)` | decimal(18,2) | No | N/A | Yes | N/A | No | No | `Full Load` | Deductible amount. |

## 10. `policy`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `policy_id` | `policy` | `policy_id` | string | string | Yes | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Unique policy identifier. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `quotation_id` | `policy` | `quotation_id` | string | string | No | `quotation.quotation_id` | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Source quotation identifier. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `customer_id` | `policy` | `customer_id` | string | string | No | `customers.customer_id` | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Customer identifier. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `provider_code` | `policy` | `provider_code` | string | string | No | `insurance_providers.provider_code` | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Insurance provider code. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `policy_number` | `policy` | `policy_number` | string | string | No | N/A | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Business policy number. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `policy_start_date` | `policy` | `policy_start_date` | date string | date | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Policy start date. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `policy_end_date` | `policy` | `policy_end_date` | date string | date | No | N/A | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Policy end date. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `policy_status` | `policy` | `policy_status` | string | string | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Policy status. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `premium_amount` | `policy` | `premium_amount` | number | decimal(18,2) | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Policy premium amount. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `issued_date` | `policy` | `issued_date` | timestamp string | timestamp | No | N/A | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Policy issued timestamp. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `last_updated` | `policy` | `last_updated` | timestamp string | timestamp | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Incremental event timestamp. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `operation_type` | `policy` | `operation_type` | string | string | No | N/A | No | Use source value; default I only for full baseline | No | No | `Full Load` for baseline; `Incremental Load` for daily files | `I = Insert`, `U = Update`, `D = Delete`. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `batch_date` | `policy` | `batch_date` | date string | date | No | N/A | No | Pipeline batch date | No | Yes | `Full Load` for baseline; `Incremental Load` for daily files | Source batch date. |
| Policy Domain Source | `N/A - JSON file` | Policy JSON file | `source_system` | `policy` | `source_system` | string | string | No | N/A | No | `policy_system` | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Source system name. |

## 11. `payment`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `payment_id` | `payment` | `payment_id` | string | string | Yes | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Unique payment identifier. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `policy_id` | `payment` | `policy_id` | string | string | No | `policy.policy_id` | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Related policy identifier. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `payment_date` | `payment` | `payment_date` | timestamp string | timestamp | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Payment timestamp. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `payment_method` | `payment` | `payment_method` | string | string | No | N/A | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Payment method. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `payment_status` | `payment` | `payment_status` | string | string | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Payment status. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `payment_amount` | `payment` | `payment_amount` | number | decimal(18,2) | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Payment amount. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `transaction_reference` | `payment` | `transaction_reference` | string | string | No | N/A | Yes | N/A | Sensitive | No | `Full Load` for baseline; `Incremental Load` for daily files | Payment transaction reference. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `last_updated` | `payment` | `last_updated` | timestamp string | timestamp | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Incremental event timestamp. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `operation_type` | `payment` | `operation_type` | string | string | No | N/A | No | Use source value; default I only for full baseline | No | No | `Full Load` for baseline; `Incremental Load` for daily files | `I = Insert`, `U = Update`, `D = Delete`. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `batch_date` | `payment` | `batch_date` | date string | date | No | N/A | No | Pipeline batch date | No | Yes | `Full Load` for baseline; `Incremental Load` for daily files | Source batch date. |
| Policy Domain Source | `N/A - JSON file` | Payment JSON file | `source_system` | `payment` | `source_system` | string | string | No | N/A | No | `payment_system` | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Source system name. |

## 12. `cancellation`

| Source Group | Source DB | Source Object | Source Column | Bronze Table | Bronze Column | Source Data Type | Bronze Data Type | Is Primary Key | Reference Table / Column | Nullable | Default Value | PII / Sensitive Flag | Partition Column | Load Type | Description |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `cancellation_id` | `cancellation` | `cancellation_id` | string | string | Yes | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Unique cancellation identifier. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `policy_id` | `cancellation` | `policy_id` | string | string | No | `policy.policy_id` | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Related policy identifier. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `cancellation_date` | `cancellation` | `cancellation_date` | timestamp string | timestamp | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Cancellation timestamp. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `cancellation_reason` | `cancellation` | `cancellation_reason` | string | string | No | N/A | Yes | N/A | Sensitive | No | `Full Load` for baseline; `Incremental Load` for daily files | Cancellation reason. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `refund_amount` | `cancellation` | `refund_amount` | number | decimal(18,2) | No | N/A | Yes | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Refund amount. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `last_updated` | `cancellation` | `last_updated` | timestamp string | timestamp | No | N/A | No | N/A | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Incremental event timestamp. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `operation_type` | `cancellation` | `operation_type` | string | string | No | N/A | No | Use source value; default I only for full baseline | No | No | `Full Load` for baseline; `Incremental Load` for daily files | `I = Insert`, `U = Update`, `D = Delete`. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `batch_date` | `cancellation` | `batch_date` | date string | date | No | N/A | No | Pipeline batch date | No | Yes | `Full Load` for baseline; `Incremental Load` for daily files | Source batch date. |
| Policy Domain Source | `N/A - JSON file` | Cancellation JSON file | `source_system` | `cancellation` | `source_system` | string | string | No | N/A | No | `policy_system` | No | No | `Full Load` for baseline; `Incremental Load` for daily files | Source system name. |

