# Data Source Survey

## Source Inventory

| No. | Source Group | Source DB | Source Object | Data Format | Expected Grain |
|---:|---|---|---|---|---|
| 1 | CRM Source: Customer | insurance_crm_db | dbo.customers | Relational Table | 1 row = 1 customer; primary key customer_id; current SQL seed has 1,000 customers. |
| 2 | CRM Source: Agent | insurance_crm_db | dbo.agents | Relational Table / Reference Data | 1 row = 1 agent; primary key agent_id; current SQL seed has 4 agents. |
| 3 | CRM Source: Provider Reference | insurance_crm_db | dbo.insurance_providers | Relational Table / Reference Data | 1 row = 1 provider; primary key provider_code; current SQL seed has 6 providers. |
| 4 | CRM Source: Vehicle | insurance_crm_db | dbo.vehicle | Relational Table | 1 row = 1 vehicle; primary key vehicle_id; current SQL seed has 1,000 vehicles. |
| 5 | CRM Source: Quotation | insurance_crm_db | dbo.quotation | Relational Table | 1 row = 1 quotation; primary key quotation_id; current SQL seed has 1,000 quotations. |
| 6 | CRM Source: Quotation Item | insurance_crm_db | dbo.quotation_item | Relational Table | 1 row = 1 quotation item; primary key quotation_item_id; current SQL seed has 1,000 quotation items. |
| 7 | Policy Domain Source: Policy | insurance_policy_db | dbo.policy_info + policy JSON files (/landing/full/2026-05-25/policy_full_2026-05-25.json, daily policy_YYYY-MM-DD.json) | Relational Source + JSON CDC File | 1 row/object = 1 policy; primary key policy_id; full JSON 2026-05-25 has 600 policies. |
| 8 | Policy Domain Source: Payment | insurance_policy_db | dbo.payment + payment JSON files (/landing/full/2026-05-25/payment_full_2026-05-25.json, daily payment_YYYY-MM-DD.json) | Relational Source + JSON CDC File | 1 row/object = 1 payment transaction; primary key payment_id; full JSON 2026-05-25 has 600 payments. |
| 9 | Policy Domain Source: Cancellation | insurance_policy_db | dbo.cancellation + cancellation JSON files (/landing/full/2026-05-25/cancellation_full_2026-05-25.json, daily cancellation_YYYY-MM-DD.json) | Relational Source + JSON CDC File | 1 row/object = 1 cancellation event; primary key cancellation_id; full JSON 2026-05-25 has 60 cancellations. |

## 1. CRM Source: Customer

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.customers |
| Business Meaning | Customer information: name, gender, date of birth, phone, email, city, district, and created_date. |
| Data Format | Relational Table |
| Expected Grain | 1 row = 1 customer; primary key customer_id; current SQL seed has 1,000 customers. |
| Relationship to Validate | customers.customer_id -> vehicle.customer_id (1:n); customers.customer_id -> quotation.customer_id (1:n); customer_id also appears in the policy domain to link policies with customers. |
| Load Pattern to Assess | Initial full load; afterward, use full snapshot/SCD comparison to capture updates/deletes. If only created_date is used, it is safe only for new inserts. |
| CDC / Watermark Questions for Source Owner | created_date exists, but there is no updated_at, is_deleted, deleted_at, or operation_type. Ask the source owner whether CDC/change tracking or a soft delete flag is available. |
| Insert / Update / Delete Scenario | Insert: new customer registration. Update: phone/email/address/profile changes. Delete: account deactivation or soft delete; currently no column represents deletes. |
| Main Data Quality Checks | customer_id NOT NULL + UNIQUE; valid email; valid phone_number; dob < current date; duplicate customer check by batch; reject null keys, cleanse email/phone. |
| Notes / Risk | CRM_Policy marks customers as slowly changing and the CDC Assessment marks Incremental Load by created_date, but created_date cannot capture updates/deletes. Risk: without snapshot or CDC, SCD changes will be missed. |

## 2. CRM Source: Agent

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.agents |
| Business Meaning | Insurance sales agent information: agent name, region, branch, manager, and created_date. |
| Data Format | Relational Table / Reference Data |
| Expected Grain | 1 row = 1 agent; primary key agent_id; current SQL seed has 4 agents. |
| Relationship to Validate | agents.agent_id -> quotation.agent_id (1:n); one agent manages many quotations. |
| Load Pattern to Assess | Reference full reload or daily full snapshot because volume is low. created_date can only identify new agents. |
| CDC / Watermark Questions for Source Owner | created_date exists, but there is no updated_at/delete flag. Ask the source owner whether agent status, active_flag, or resignation/deactivation fields exist. |
| Insert / Update / Delete Scenario | Insert: new insurance agent onboarded. Update: branch/manager reassignment. Delete: resignation/deactivation. |
| Main Data Quality Checks | agent_id NOT NULL + UNIQUE; agent_name not missing; region/branch/manager length valid; relationship agent_id must match quotation.agent_id. |
| Notes / Risk | Source Inventory marks Incremental(created_date), while CDC Assessment marks Full Load. Because there is no updated_at, full/reference reload is safer for Bronze. |

## 3. CRM Source: Provider Reference

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.insurance_providers |
| Business Meaning | Insurance provider reference data: provider code, name, group, and active_flag. |
| Data Format | Relational Table / Reference Data |
| Expected Grain | 1 row = 1 provider; primary key provider_code; current SQL seed has 6 providers. |
| Relationship to Validate | insurance_providers.provider_code -> quotation.provider_code (1:n); provider_code also links to policy.provider_code. |
| Load Pattern to Assess | Reference full reload or full snapshot because changes are very low. Do not use incremental because there is no watermark. |
| CDC / Watermark Questions for Source Owner | No watermark column. active_flag is a business status, not CDC. Ask the source owner for the rule for inactive/deleted providers. |
| Insert / Update / Delete Scenario | Insert: new provider partnership. Update: provider status/group update. Delete: inactive/decommissioned provider. |
| Main Data Quality Checks | provider_code NOT NULL + UNIQUE; active_flag valid 0/1; provider_name not missing; relationship provider_code must match quotation/policy. |
| Notes / Risk | Low-change reference table; full reload is simpler and lower risk than incremental. |

## 4. CRM Source: Vehicle

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.vehicle |
| Business Meaning | Customer vehicle information: plate number, brand, model, manufacture year, and vehicle value. |
| Data Format | Relational Table |
| Expected Grain | 1 row = 1 vehicle; primary key vehicle_id; current SQL seed has 1,000 vehicles. |
| Relationship to Validate | vehicle.customer_id -> customers.customer_id (n:1); one customer can own many vehicles. |
| Load Pattern to Assess | Initial full load; afterward, use full snapshot comparison because the table has no watermark. If the source adds updated_at/delete flag, switch to incremental CDC/merge. |
| CDC / Watermark Questions for Source Owner | No created_at/updated_at/is_deleted. Ask the source owner how to identify plate/value updates and vehicles sold/removed. |
| Insert / Update / Delete Scenario | Insert: customer registers a new vehicle. Update: plate number/car value/model update. Delete: vehicle sold or removed. |
| Main Data Quality Checks | vehicle_id NOT NULL + UNIQUE; plate_number UNIQUE; manufacture_year <= current year; vehicle_value >= 0; customer_id must exist in customers. |
| Notes / Risk | CRM_Policy marks Incremental, but the current schema has no watermark. Bronze should store snapshots by batch so Silver can compare changes. |

## 5. CRM Source: Quotation

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.quotation |
| Business Meaning | Insurance quotation information: customer, agent, provider, quotation date/status, package, premium, and expiry date. |
| Data Format | Relational Table |
| Expected Grain | 1 row = 1 quotation; primary key quotation_id; current SQL seed has 1,000 quotations. |
| Relationship to Validate | quotation.customer_id -> customers; quotation.agent_id -> agents; quotation.provider_code -> insurance_providers; quotation.quotation_id -> quotation_item (1:n); quotation -> policy_info (1:0/1) when quotation_status=CONVERTED. |
| Load Pattern to Assess | Initial full load; incremental merge is accurate only if updated_at/CDC exists. With the current schema, quotation_date captures only new inserts; use snapshot comparison for status updates/deletes. |
| CDC / Watermark Questions for Source Owner | quotation_date and quotation_expiry_date exist, but there is no updated_at/delete flag. Ask the source owner for a watermark for status changes and expiration cleanup. |
| Insert / Update / Delete Scenario | Insert: new quotation generated. Update: quotation_status changes. Delete: expiration cleanup. |
| Main Data Quality Checks | quotation_id NOT NULL + UNIQUE; quotation_date <= current date; quotation_status valid; premium_amount >= 0; FK customer/agent/provider must match; only converted quotations can link to policies. |
| Notes / Risk | CDC Assessment marks Incremental MERGE Load, but without updated_at there is a risk of missing status updates if filtering only by quotation_date. |

## 6. CRM Source: Quotation Item

| Field | Value |
|---|---|
| Source System / Location | SQL Server / insurance_crm_db |
| Source DB | insurance_crm_db |
| Source Object | dbo.quotation_item |
| Business Meaning | Quotation coverage details: coverage type, coverage amount, and deductible amount. |
| Data Format | Relational Table |
| Expected Grain | 1 row = 1 quotation item; primary key quotation_item_id; current SQL seed has 1,000 quotation items. |
| Relationship to Validate | quotation_item.quotation_id -> quotation.quotation_id (n:1); one quotation has many coverage details. |
| Load Pattern to Assess | Initial full load; afterward, use full snapshot comparison because there is no watermark. If coverage items are immutable, incremental append by quotation_id/batch may be possible, but source owner confirmation is required. |
| CDC / Watermark Questions for Source Owner | No watermark column. Ask the source owner how coverage updates/deletes are detected. |
| Insert / Update / Delete Scenario | Insert: new coverage item added. Update: coverage/deductible amount adjustment. Delete: coverage removed from quotation. |
| Main Data Quality Checks | quotation_item_id NOT NULL + UNIQUE; quotation_id FK match; coverage_amount >= 0; deductible_amount >= 0. |
| Notes / Risk | CDC Assessment marks Full Snapshot Load, which matches the current schema. |

## 7. Policy Domain Source: Policy

| Field | Value |
|---|---|
| Source System / Location | Policy Domain / SQL Server insurance_policy_db + JSON Landing |
| Source DB | insurance_policy_db |
| Source Object | dbo.policy_info + policy JSON files (/landing/full/2026-05-25/policy_full_2026-05-25.json, daily policy_YYYY-MM-DD.json) |
| Business Meaning | Official insurance policy contract: quotation/customer/provider, policy number, start/end date, status, premium, and issued date. |
| Data Format | Relational Source + JSON CDC File |
| Expected Grain | 1 row/object = 1 policy; primary key policy_id; full JSON 2026-05-25 has 600 policies. |
| Relationship to Validate | policy_info.quotation_id -> quotation.quotation_id (1:0/1 when converted); policy.customer_id -> customers; policy.provider_code -> insurance_providers; policy.policy_id -> payment/cancellation (1:n). |
| Load Pattern to Assess | Use the JSON full file as the baseline; use daily JSON for incremental CDC by operation_type + last_updated + batch_date. Do not load duplicate SQL and JSON data directly into two separate Bronze tables. |
| CDC / Watermark Questions for Source Owner | JSON has last_updated, operation_type, batch_date, and source_system. SQL policy_info has no updated_at/operation_type, so JSON CDC is the main source path. Confirm timezone and ordering when last_updated values are duplicated. |
| Insert / Update / Delete Scenario | Insert: operation_type=I, for example a new policy issued/POL900001. Update: operation_type=U, policy_status changes. Delete: operation_type=D, hard delete such as the POL00555 delete event. |
| Main Data Quality Checks | policy_id NOT NULL + UNIQUE; policy_number UNIQUE; issued_date <= current date; premium_amount >= 0; policy_status valid; operation_type I/U/D; FK quotation/customer/provider; policy_start_date <= policy_end_date. |
| Notes / Risk | Merged insurance_policy_db and JSON because they contain the same data/function. Full JSON profiling: 600 rows, no nulls/duplicates; status ACTIVE/CANCELLED/EXPIRED/ISSUED has 150 each. If loading directly from SQL, CDC metadata is missing. |

## 8. Policy Domain Source: Payment

| Field | Value |
|---|---|
| Source System / Location | Policy Domain / SQL Server insurance_policy_db + JSON Landing |
| Source DB | insurance_policy_db |
| Source Object | dbo.payment + payment JSON files (/landing/full/2026-05-25/payment_full_2026-05-25.json, daily payment_YYYY-MM-DD.json) |
| Business Meaning | Policy payment transaction: payment date, method, status, amount, and transaction reference. |
| Data Format | Relational Source + JSON CDC File |
| Expected Grain | 1 row/object = 1 payment transaction; primary key payment_id; full JSON 2026-05-25 has 600 payments. |
| Relationship to Validate | payment.policy_id -> policy_info/policy.policy_id (n:1); payment_amount should reconcile with policy premium; transaction_reference is an alternate key/gateway reference. |
| Load Pattern to Assess | Use the JSON full file as the baseline; use daily JSON for incremental CDC/append by operation_type + last_updated + batch_date. payment_date is a business event date and is not sufficient for status updates if last_updated is missing. |
| CDC / Watermark Questions for Source Owner | JSON has last_updated, operation_type, batch_date, and source_system. Confirm whether payments can generate operation_type=D/reversal and whether transaction_reference is immutable. |
| Insert / Update / Delete Scenario | Insert: operation_type=I, new payment transaction/PAY900001. Update: operation_type=U, payment_status update such as PAY00200 -> FAILED. Delete: operation_type=D if a reversal/delete event exists. |
| Main Data Quality Checks | payment_id NOT NULL + UNIQUE; transaction_reference UNIQUE; payment_amount >= 0; payment_date <= current date; payment_status valid; operation_type I/U/D; policy_id must match policy. |
| Notes / Risk | Full JSON profiling: 600 rows, no nulls/duplicates; 0 missing policy_id; payment_amount matches premium 600/600. Risk: FAILED/REFUNDED still has a positive amount, so distinguish attempted amount from settled amount. |

## 9. Policy Domain Source: Cancellation

| Field | Value |
|---|---|
| Source System / Location | Policy Domain / SQL Server insurance_policy_db + JSON Landing |
| Source DB | insurance_policy_db |
| Source Object | dbo.cancellation + cancellation JSON files (/landing/full/2026-05-25/cancellation_full_2026-05-25.json, daily cancellation_YYYY-MM-DD.json) |
| Business Meaning | Policy cancellation and refund event: cancellation date, reason, and refund amount. |
| Data Format | Relational Source + JSON CDC File |
| Expected Grain | 1 row/object = 1 cancellation event; primary key cancellation_id; full JSON 2026-05-25 has 60 cancellations. |
| Relationship to Validate | cancellation.policy_id -> policy_info/policy.policy_id (n:1); cancellation event must reconcile with policy_status=CANCELLED and refund/payment. |
| Load Pattern to Assess | Use the JSON full file as the baseline; use daily JSON for incremental CDC/event append by operation_type + last_updated + batch_date. cancellation_date is the business event time. |
| CDC / Watermark Questions for Source Owner | JSON has last_updated, operation_type, batch_date, and source_system. Confirm whether cancellation update/delete/reversal events exist and how late-arriving events are handled. |
| Insert / Update / Delete Scenario | Insert: operation_type=I, new cancellation event/CAN900001. Update: operation_type=U, refund adjustment/review. Delete: operation_type=D, deletion/reversal if generated by the source. |
| Main Data Quality Checks | cancellation_id NOT NULL + UNIQUE; cancellation_date <= current date; refund_amount >= 0; operation_type I/U/D; policy_id must match policy; cancellation_date >= policy_start_date; policy_status must be synchronized. |
| Notes / Risk | Full JSON profiling: 60 rows, no nulls/duplicates; 0 missing policy_id; refund_amount = 1,000,000. Major risk: among 60 cancellations, only 30 policies have status CANCELLED while 30 are still ACTIVE, so a reconciliation rule is required. |
