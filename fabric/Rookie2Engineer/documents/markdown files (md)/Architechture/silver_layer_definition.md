# Define Silver Layer

## 1. Purpose

Silver layer is the cleaned, standardized, deduplicated, and conformed layer built from Bronze.

Bronze keeps raw snapshots/events. Silver standardizes data types and values, resolves duplicates, validates business rules and relationships, and creates business-ready current-state tables for downstream Gold reporting.

## 2. Silver Input And Output

| Source Group | Bronze Input | Silver Output | Processing Style |
|---|---|---|---|
| CRM Source | `customers` | `customers` | Snapshot dedupe + current-state merge |
| CRM Source | `agents` | `agents` | Reference dedupe + current-state merge |
| CRM Source | `insurance_providers` | `insurance_providers` | Reference dedupe + current-state merge |
| CRM Source | `vehicle` | `vehicle` | Snapshot dedupe + current-state merge |
| CRM Source | `quotation` | `quotation` | Snapshot dedupe + current-state merge |
| CRM Source | `quotation_item` | `quotation_item` | Snapshot dedupe + current-state merge |
| Policy Domain Source | `policy` | `policy` | Change event merge using `operation_type` |
| Policy Domain Source | `payment` | `payment` | Change event merge using `operation_type` |
| Policy Domain Source | `cancellation` | `cancellation` | Change event merge using `operation_type` |


## 3. Silver Load Rules

### CRM Source Tables

CRM tables are loaded to Bronze as full snapshots/reference reloads because the SQL schema does not provide reliable `updated_at`, `operation_type`, or delete flag.

Silver processing for CRM tables:

1. Read latest Bronze batch by `_batch_date`.
2. Deduplicate by primary key within the batch.
3. Standardize data types and text values.
4. Apply table-level validation and relationship rules.
5. Compare current batch hash with existing Silver current record.
6. Insert new records, update changed records, and mark missing records as `_is_deleted = true` only if business confirms snapshot missing means delete.

### Policy Domain Tables

Policy, payment, and cancellation use JSON change event files from Bronze. No database CDC is enabled or assumed.

Silver processing for Policy Domain:

1. Read Bronze events by `batch_date`.
2. Deduplicate repeated events by primary key, `last_updated`, `operation_type`, and `_source_file_name`.
3. Process events in order by `last_updated`, then `_ingestion_timestamp`.
4. Apply `operation_type`:

| operation_type | Silver Action |
|---|---|
| `I` | Insert new current record. If key already exists, treat as idempotent insert or compare hash. |
| `U` | Update existing current record. If key does not exist, treat as late-arriving upsert only when the project rule allows it. |
| `D` | Mark current record as `_is_deleted = true` and `_is_current = false`. Do not physically delete from Silver. |

## 4. Silver Table Definitions

### `customers`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `customer_id` | string | Yes | N/A | Unique current customer. | No | Customer identifier. |
| `full_name` | string | No | N/A | Trim; length <= 200. | PII | Customer full name. |
| `gender` | string | No | N/A | Standardize accepted gender values. | Sensitive | Customer gender. |
| `dob` | date | No | N/A | Must be before current date. | PII | Date of birth. |
| `phone_number` | string | No | N/A | Valid phone format where possible. | PII | Customer phone. |
| `email` | string | No | N/A | Valid email format where possible. | PII | Customer email. |
| `city` | string | No | N/A | Trim; length <= 100. | No | City. |
| `district` | string | No | N/A | Trim; length <= 100. | No | District. |
| `created_date` | timestamp | No | N/A | Valid timestamp. | No | Customer created timestamp. |

### `agents`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `agent_id` | string | Yes | N/A | Unique current agent. | No | Agent identifier. |
| `agent_name` | string | No | N/A | Trim; length <= 200. | PII | Agent name. |
| `region` | string | No | N/A | Trim; length <= 100. | No | Sales region. |
| `branch` | string | No | N/A | Trim; length <= 100. | No | Branch. |
| `manager_name` | string | No | N/A | Trim; length <= 200. | PII | Manager name. |
| `created_date` | timestamp | No | N/A | Valid timestamp. | No | Agent created timestamp. |

### `insurance_providers`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `provider_code` | string | Yes | N/A | Unique current provider. | No | Provider code. |
| `provider_name` | string | No | N/A | Trim; length <= 200. | No | Provider name. |
| `provider_group` | string | No | N/A | Trim; length <= 100. | No | Provider group. |
| `active_flag` | int | No | N/A | Expected values: 0 or 1. | No | Active/inactive flag. |

### `vehicle`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `vehicle_id` | string | Yes | N/A | Unique current vehicle. | No | Vehicle identifier. |
| `customer_id` | string | No | `customers.customer_id` | Must exist in `customers`. | No | Owner customer identifier. |
| `plate_number` | string | No | N/A | Duplicate check; length <= 20. | Sensitive | Plate number. |
| `vehicle_brand` | string | No | N/A | Trim; length <= 100. | No | Vehicle brand. |
| `vehicle_model` | string | No | N/A | Trim; length <= 100. | No | Vehicle model. |
| `manufacture_year` | int | No | N/A | Must be <= current year. | No | Manufacture year. |
| `vehicle_value` | decimal(18,2) | No | N/A | Must be >= 0. | No | Vehicle value. |

### `quotation`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `quotation_id` | string | Yes | N/A | Unique current quotation. | No | Quotation identifier. |
| `customer_id` | string | No | `customers.customer_id` | Must exist in `customers`. | No | Customer identifier. |
| `agent_id` | string | No | `agents.agent_id` | Must exist in `agents`. | No | Agent identifier. |
| `provider_code` | string | No | `insurance_providers.provider_code` | Must exist in `insurance_providers`. | No | Provider code. |
| `quotation_date` | timestamp | No | N/A | Must be <= current timestamp. | No | Quotation date. |
| `quotation_status` | string | No | N/A | Expected values: CONVERTED, ACCEPTED, REJECTED, EXPIRED, QUOTED. | No | Quotation status. |
| `package_code` | string | No | N/A | Expected values: BASIC, STANDARD, PREMIUM, VIP. | No | Package code. |
| `premium_amount` | decimal(18,2) | No | N/A | Must be >= 0. | No | Quoted premium amount. |
| `quotation_expiry_date` | timestamp | No | N/A | Should be >= `quotation_date`. | No | Quotation expiry timestamp. |

### `quotation_item`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `quotation_item_id` | string | Yes | N/A | Unique current quotation item. | No | Quotation item identifier. |
| `quotation_id` | string | No | `quotation.quotation_id` | Must exist in `quotation`. | No | Parent quotation identifier. |
| `coverage_type` | string | No | N/A | Trim; length <= 100. | No | Coverage type. |
| `coverage_amount` | decimal(18,2) | No | N/A | Must be >= 0. | No | Coverage amount. |
| `deductible_amount` | decimal(18,2) | No | N/A | Must be >= 0. | No | Deductible amount. |

### `policy`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `policy_id` | string | Yes | N/A | Unique current non-deleted policy. | No | Policy identifier. |
| `quotation_id` | string | No | `quotation.quotation_id` | Must exist in `quotation`; quotation should be converted. | No | Source quotation identifier. |
| `customer_id` | string | No | `customers.customer_id` | Must exist in `customers`. | No | Customer identifier. |
| `provider_code` | string | No | `insurance_providers.provider_code` | Must exist in `insurance_providers`. | No | Provider code. |
| `policy_number` | string | No | N/A | Unique current policy number. | No | Policy number. |
| `policy_start_date` | date | No | N/A | Valid date. | No | Policy start date. |
| `policy_end_date` | date | No | N/A | Must be >= `policy_start_date`. | No | Policy end date. |
| `policy_status` | string | No | N/A | Expected values: ACTIVE, CANCELLED, EXPIRED, ISSUED. | No | Policy status. |
| `premium_amount` | decimal(18,2) | No | N/A | Must be >= 0. | No | Policy premium. |
| `issued_date` | timestamp | No | N/A | Must be <= current timestamp. | No | Policy issued timestamp. |
| `last_updated` | timestamp | No | N/A | Valid source update timestamp. | No | Source update timestamp. |

### `payment`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `payment_id` | string | Yes | N/A | Unique current non-deleted payment. | No | Payment identifier. |
| `policy_id` | string | No | `policy.policy_id` | Must exist in `policy`. | No | Related policy identifier. |
| `payment_date` | timestamp | No | N/A | Must be <= current timestamp. | No | Payment timestamp. |
| `payment_method` | string | No | N/A | Expected values: Bank Transfer, Credit Card, E-wallet. | No | Payment method. |
| `payment_status` | string | No | N/A | Expected values: PAID, FAILED, PENDING, REFUNDED. | No | Payment status. |
| `payment_amount` | decimal(18,2) | No | N/A | Must be >= 0. | No | Payment amount. |
| `transaction_reference` | string | No | N/A | Unique current transaction reference. | Sensitive | Payment transaction reference. |
| `last_updated` | timestamp | No | N/A | Valid source update timestamp. | No | Source update timestamp. |

### `cancellation`

| Column | Data Type | Primary Key | Reference Table / Column | Validation Rule | PII / Sensitive Flag | Description |
| --- | --- | --- | --- | --- | --- | --- |
| `cancellation_id` | string | Yes | N/A | Unique current non-deleted cancellation. | No | Cancellation identifier. |
| `policy_id` | string | No | `policy.policy_id` | Must exist in `policy`. | No | Related policy identifier. |
| `cancellation_date` | timestamp | No | N/A | Must be <= current timestamp and >= policy start date. | No | Cancellation timestamp. |
| `cancellation_reason` | string | No | N/A | Not blank; trim text. | Sensitive | Cancellation reason. |
| `refund_amount` | decimal(18,2) | No | N/A | Must be >= 0 and should be <= paid/premium amount. | No | Refund amount. |
| `last_updated` | timestamp | No | N/A | Valid source update timestamp. | No | Source update timestamp. |

## 5. Relationship Rules

| Relationship | Silver Rule |
|---|---|
| `vehicle.customer_id -> customers.customer_id` | Customer must exist. |
| `quotation.customer_id -> customers.customer_id` | Customer must exist. |
| `quotation.agent_id -> agents.agent_id` | Agent must exist. |
| `quotation.provider_code -> insurance_providers.provider_code` | Provider must exist. |
| `quotation_item.quotation_id -> quotation.quotation_id` | Quotation must exist. |
| `policy.quotation_id -> quotation.quotation_id` | Quotation must exist and should have `quotation_status = CONVERTED`. |
| `payment.policy_id -> policy.policy_id` | Policy must exist. |
| `cancellation.policy_id -> policy.policy_id` | Policy must exist. |

## 6. Cross-Table Reconciliation Rules

| Rule | Description |
|---|---|
| Policy premium vs payment amount | `payment.payment_amount` should reconcile with `policy.premium_amount` for normal full-payment cases. |
| Cancellation vs policy status | A policy with cancellation event should eventually have `policy_status = CANCELLED`. |
| Refund amount vs paid/premium amount | `refund_amount` should not exceed paid amount or policy premium. |
| Quotation converted to policy | A policy should link to a quotation with `quotation_status = CONVERTED`. |

## 7. Final Silver Decision

| Area | Decision |
|---|---|
| CRM Source | Build Silver current-state tables from Bronze full snapshots/reference reloads. Use hashes to detect changes. |
| Policy Domain Source | Build Silver current-state tables by applying JSON change events with `operation_type = I/U/D`. |
| Deletes | Use logical delete in Silver with `_is_deleted = true`; do not physically delete. |
| Relationships | Validate relationship consistency in Silver current-state tables. |
| Output for Gold | Gold should consume Silver current records where `_is_current = true` and `_is_deleted = false`. |
