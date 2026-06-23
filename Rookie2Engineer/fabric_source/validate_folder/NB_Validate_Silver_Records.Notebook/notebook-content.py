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

# MARKDOWN ********************

# # **# 1. Bronze -> Silver row-count reconciliation.**

# CELL ********************

# MAGIC %%sql
# MAGIC WITH bronze_metrics AS (
# MAGIC     SELECT
# MAGIC         'customers' AS table_name,
# MAGIC         'customer_id' AS key_column,
# MAGIC         COUNT(*) AS bronze_row_count,
# MAGIC         COUNT(DISTINCT CAST(customer_id AS STRING)) AS bronze_distinct_key_count,
# MAGIC         SUM(CASE WHEN customer_id IS NULL OR TRIM(CAST(customer_id AS STRING)) = '' THEN 1 ELSE 0 END) AS bronze_blank_key_count
# MAGIC     FROM bronze.customers
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'agents',
# MAGIC         'agent_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(agent_id AS STRING)),
# MAGIC         SUM(CASE WHEN agent_id IS NULL OR TRIM(CAST(agent_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.agents
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'insurance_providers',
# MAGIC         'provider_code',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(provider_code AS STRING)),
# MAGIC         SUM(CASE WHEN provider_code IS NULL OR TRIM(CAST(provider_code AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.insurance_providers
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'vehicle',
# MAGIC         'vehicle_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(vehicle_id AS STRING)),
# MAGIC         SUM(CASE WHEN vehicle_id IS NULL OR TRIM(CAST(vehicle_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.vehicle
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation',
# MAGIC         'quotation_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(quotation_id AS STRING)),
# MAGIC         SUM(CASE WHEN quotation_id IS NULL OR TRIM(CAST(quotation_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.quotation
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation_item',
# MAGIC         'quotation_item_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(quotation_item_id AS STRING)),
# MAGIC         SUM(CASE WHEN quotation_item_id IS NULL OR TRIM(CAST(quotation_item_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.quotation_item
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy',
# MAGIC         'policy_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(policy_id AS STRING)),
# MAGIC         SUM(CASE WHEN policy_id IS NULL OR TRIM(CAST(policy_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.policy
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'payment',
# MAGIC         'payment_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(payment_id AS STRING)),
# MAGIC         SUM(CASE WHEN payment_id IS NULL OR TRIM(CAST(payment_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.payment
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'cancellation',
# MAGIC         'cancellation_id',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(cancellation_id AS STRING)),
# MAGIC         SUM(CASE WHEN cancellation_id IS NULL OR TRIM(CAST(cancellation_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM bronze.cancellation
# MAGIC ),
# MAGIC silver_metrics AS (
# MAGIC     SELECT
# MAGIC         'customers' AS table_name,
# MAGIC         COUNT(*) AS silver_row_count,
# MAGIC         COUNT(DISTINCT CAST(customer_id AS STRING)) AS silver_distinct_key_count,
# MAGIC         SUM(CASE WHEN customer_id IS NULL OR TRIM(CAST(customer_id AS STRING)) = '' THEN 1 ELSE 0 END) AS silver_blank_key_count
# MAGIC     FROM silver.customers
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'agents',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(agent_id AS STRING)),
# MAGIC         SUM(CASE WHEN agent_id IS NULL OR TRIM(CAST(agent_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.agents
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'insurance_providers',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(provider_code AS STRING)),
# MAGIC         SUM(CASE WHEN provider_code IS NULL OR TRIM(CAST(provider_code AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.insurance_providers
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'vehicle',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(vehicle_id AS STRING)),
# MAGIC         SUM(CASE WHEN vehicle_id IS NULL OR TRIM(CAST(vehicle_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.vehicle
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(quotation_id AS STRING)),
# MAGIC         SUM(CASE WHEN quotation_id IS NULL OR TRIM(CAST(quotation_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.quotation
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation_item',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(quotation_item_id AS STRING)),
# MAGIC         SUM(CASE WHEN quotation_item_id IS NULL OR TRIM(CAST(quotation_item_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.quotation_item
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(policy_id AS STRING)),
# MAGIC         SUM(CASE WHEN policy_id IS NULL OR TRIM(CAST(policy_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.policy
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'payment',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(payment_id AS STRING)),
# MAGIC         SUM(CASE WHEN payment_id IS NULL OR TRIM(CAST(payment_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.payment
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'cancellation',
# MAGIC         COUNT(*),
# MAGIC         COUNT(DISTINCT CAST(cancellation_id AS STRING)),
# MAGIC         SUM(CASE WHEN cancellation_id IS NULL OR TRIM(CAST(cancellation_id AS STRING)) = '' THEN 1 ELSE 0 END)
# MAGIC     FROM silver.cancellation
# MAGIC )
# MAGIC SELECT
# MAGIC     b.table_name,
# MAGIC     b.key_column,
# MAGIC     b.bronze_row_count,
# MAGIC     b.bronze_distinct_key_count,
# MAGIC     b.bronze_blank_key_count,
# MAGIC     s.silver_row_count,
# MAGIC     s.silver_distinct_key_count,
# MAGIC     s.silver_blank_key_count,
# MAGIC     s.silver_row_count - b.bronze_distinct_key_count AS silver_minus_bronze_distinct_keys,
# MAGIC     s.silver_row_count - s.silver_distinct_key_count AS silver_duplicate_rows,
# MAGIC     CASE
# MAGIC         WHEN s.silver_row_count > b.bronze_distinct_key_count THEN 'CHECK: Silver has more rows than Bronze distinct keys. Possible append/recovery duplicate.'
# MAGIC         WHEN s.silver_row_count < b.bronze_distinct_key_count THEN 'REVIEW: Silver has fewer rows than Bronze distinct keys. Could be expected from validation/reference filtering.'
# MAGIC         WHEN s.silver_row_count <> s.silver_distinct_key_count THEN 'CHECK: Silver has duplicate keys.'
# MAGIC         WHEN s.silver_blank_key_count > 0 THEN 'CHECK: Silver has blank/null keys.'
# MAGIC         ELSE 'OK'
# MAGIC     END AS check_note
# MAGIC FROM bronze_metrics b
# MAGIC JOIN silver_metrics s
# MAGIC     ON b.table_name = s.table_name
# MAGIC ORDER BY b.table_name;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # **2. Duplicate primary key summary.**
# 
# Expected: duplicate_key_count = 0 and extra_duplicate_rows = 0 for every table.

# CELL ********************

# MAGIC %%sql
# MAGIC WITH duplicate_keys AS (
# MAGIC     SELECT 'customers' AS table_name, 'customer_id' AS key_column, CAST(customer_id AS STRING) AS key_value, COUNT(*) AS duplicate_count
# MAGIC     FROM silver.customers
# MAGIC     GROUP BY customer_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'agents', 'agent_id', CAST(agent_id AS STRING), COUNT(*)
# MAGIC     FROM silver.agents
# MAGIC     GROUP BY agent_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'insurance_providers', 'provider_code', CAST(provider_code AS STRING), COUNT(*)
# MAGIC     FROM silver.insurance_providers
# MAGIC     GROUP BY provider_code
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'vehicle', 'vehicle_id', CAST(vehicle_id AS STRING), COUNT(*)
# MAGIC     FROM silver.vehicle
# MAGIC     GROUP BY vehicle_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'quotation', 'quotation_id', CAST(quotation_id AS STRING), COUNT(*)
# MAGIC     FROM silver.quotation
# MAGIC     GROUP BY quotation_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'quotation_item', 'quotation_item_id', CAST(quotation_item_id AS STRING), COUNT(*)
# MAGIC     FROM silver.quotation_item
# MAGIC     GROUP BY quotation_item_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'policy', 'policy_id', CAST(policy_id AS STRING), COUNT(*)
# MAGIC     FROM silver.policy
# MAGIC     GROUP BY policy_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'payment', 'payment_id', CAST(payment_id AS STRING), COUNT(*)
# MAGIC     FROM silver.payment
# MAGIC     GROUP BY payment_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'cancellation', 'cancellation_id', CAST(cancellation_id AS STRING), COUNT(*)
# MAGIC     FROM silver.cancellation
# MAGIC     GROUP BY cancellation_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC ),
# MAGIC silver_tables AS (
# MAGIC     SELECT 'customers' AS table_name, 'customer_id' AS key_column
# MAGIC     UNION ALL SELECT 'agents', 'agent_id'
# MAGIC     UNION ALL SELECT 'insurance_providers', 'provider_code'
# MAGIC     UNION ALL SELECT 'vehicle', 'vehicle_id'
# MAGIC     UNION ALL SELECT 'quotation', 'quotation_id'
# MAGIC     UNION ALL SELECT 'quotation_item', 'quotation_item_id'
# MAGIC     UNION ALL SELECT 'policy', 'policy_id'
# MAGIC     UNION ALL SELECT 'payment', 'payment_id'
# MAGIC     UNION ALL SELECT 'cancellation', 'cancellation_id'
# MAGIC )
# MAGIC SELECT
# MAGIC     'DUPLICATE_PK' AS check_type,
# MAGIC     CASE WHEN COUNT(d.key_value) = 0 THEN 'PASS' ELSE 'CHECK' END AS status,
# MAGIC     t.table_name,
# MAGIC     t.key_column,
# MAGIC     COUNT(d.key_value) AS duplicate_key_count,
# MAGIC     COALESCE(SUM(d.duplicate_count - 1), 0) AS extra_duplicate_rows,
# MAGIC     'Expected: no duplicate business key in Silver' AS expected_result
# MAGIC FROM silver_tables t
# MAGIC LEFT JOIN duplicate_keys d
# MAGIC     ON t.table_name = d.table_name
# MAGIC GROUP BY t.table_name, t.key_column
# MAGIC ORDER BY
# MAGIC     CASE WHEN COUNT(d.key_value) = 0 THEN 1 ELSE 0 END,
# MAGIC     extra_duplicate_rows DESC,
# MAGIC     t.table_name;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # **2.1 Duplicate primary key detail.**
# 
# Run/read this when section 2 status = CHECK.

# CELL ********************

# MAGIC %%sql
# MAGIC WITH duplicate_keys AS (
# MAGIC     SELECT 'customers' AS table_name, 'customer_id' AS key_column, CAST(customer_id AS STRING) AS key_value, COUNT(*) AS duplicate_count
# MAGIC     FROM silver.customers
# MAGIC     GROUP BY customer_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'agents', 'agent_id', CAST(agent_id AS STRING), COUNT(*)
# MAGIC     FROM silver.agents
# MAGIC     GROUP BY agent_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'insurance_providers', 'provider_code', CAST(provider_code AS STRING), COUNT(*)
# MAGIC     FROM silver.insurance_providers
# MAGIC     GROUP BY provider_code
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'vehicle', 'vehicle_id', CAST(vehicle_id AS STRING), COUNT(*)
# MAGIC     FROM silver.vehicle
# MAGIC     GROUP BY vehicle_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'quotation', 'quotation_id', CAST(quotation_id AS STRING), COUNT(*)
# MAGIC     FROM silver.quotation
# MAGIC     GROUP BY quotation_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'quotation_item', 'quotation_item_id', CAST(quotation_item_id AS STRING), COUNT(*)
# MAGIC     FROM silver.quotation_item
# MAGIC     GROUP BY quotation_item_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'policy', 'policy_id', CAST(policy_id AS STRING), COUNT(*)
# MAGIC     FROM silver.policy
# MAGIC     GROUP BY policy_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'payment', 'payment_id', CAST(payment_id AS STRING), COUNT(*)
# MAGIC     FROM silver.payment
# MAGIC     GROUP BY payment_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT 'cancellation', 'cancellation_id', CAST(cancellation_id AS STRING), COUNT(*)
# MAGIC     FROM silver.cancellation
# MAGIC     GROUP BY cancellation_id
# MAGIC     HAVING COUNT(*) > 1
# MAGIC )
# MAGIC SELECT
# MAGIC     'DUPLICATE_PK_DETAIL' AS check_type,
# MAGIC     table_name,
# MAGIC     key_column,
# MAGIC     key_value,
# MAGIC     duplicate_count,
# MAGIC     duplicate_count - 1 AS extra_duplicate_rows
# MAGIC FROM duplicate_keys
# MAGIC ORDER BY table_name, duplicate_count DESC, key_value;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # **3. Reference/orphan records Silver tables.**
# 
# Expected: duplicate_current_key_count = 0.

# CELL ********************

# MAGIC %%sql
# MAGIC 
# MAGIC WITH reference_checks AS (
# MAGIC     SELECT
# MAGIC         'vehicle.customer_id -> customers.customer_id' AS check_name,
# MAGIC         COUNT(*) AS orphan_count
# MAGIC     FROM silver.vehicle v
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON v.customer_id = c.customer_id
# MAGIC     WHERE v.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(v.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.customer_id -> customers.customer_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON q.customer_id = c.customer_id
# MAGIC     WHERE q.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(q.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.agent_id -> agents.agent_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.agents a
# MAGIC         ON q.agent_id = a.agent_id
# MAGIC     WHERE q.agent_id IS NOT NULL
# MAGIC       AND TRIM(CAST(q.agent_id AS STRING)) <> ''
# MAGIC       AND a.agent_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.provider_code -> insurance_providers.provider_code',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.insurance_providers p
# MAGIC         ON q.provider_code = p.provider_code
# MAGIC     WHERE q.provider_code IS NOT NULL
# MAGIC       AND TRIM(CAST(q.provider_code AS STRING)) <> ''
# MAGIC       AND p.provider_code IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation_item.quotation_id -> quotation.quotation_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.quotation_item qi
# MAGIC     LEFT JOIN silver.quotation q
# MAGIC         ON qi.quotation_id = q.quotation_id
# MAGIC     WHERE qi.quotation_id IS NOT NULL
# MAGIC       AND TRIM(CAST(qi.quotation_id AS STRING)) <> ''
# MAGIC       AND q.quotation_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.quotation_id -> quotation.quotation_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.quotation q
# MAGIC         ON p.quotation_id = q.quotation_id
# MAGIC     WHERE p.quotation_id IS NOT NULL
# MAGIC       AND TRIM(CAST(p.quotation_id AS STRING)) <> ''
# MAGIC       AND q.quotation_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.customer_id -> customers.customer_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON p.customer_id = c.customer_id
# MAGIC     WHERE p.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(p.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.provider_code -> insurance_providers.provider_code',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.insurance_providers ip
# MAGIC         ON p.provider_code = ip.provider_code
# MAGIC     WHERE p.provider_code IS NOT NULL
# MAGIC       AND TRIM(CAST(p.provider_code AS STRING)) <> ''
# MAGIC       AND ip.provider_code IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'payment.policy_id -> policy.policy_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.payment pay
# MAGIC     LEFT JOIN silver.policy pol
# MAGIC         ON pay.policy_id = pol.policy_id
# MAGIC     WHERE pay.policy_id IS NOT NULL
# MAGIC       AND TRIM(CAST(pay.policy_id AS STRING)) <> ''
# MAGIC       AND pol.policy_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'cancellation.policy_id -> policy.policy_id',
# MAGIC         COUNT(*)
# MAGIC     FROM silver.cancellation can
# MAGIC     LEFT JOIN silver.policy pol
# MAGIC         ON can.policy_id = pol.policy_id
# MAGIC     WHERE can.policy_id IS NOT NULL
# MAGIC       AND TRIM(CAST(can.policy_id AS STRING)) <> ''
# MAGIC       AND pol.policy_id IS NULL
# MAGIC )
# MAGIC SELECT
# MAGIC     'REFERENCE_INTEGRITY' AS check_type,
# MAGIC     CASE WHEN orphan_count = 0 THEN 'PASS' ELSE 'CHECK' END AS status,
# MAGIC     check_name,
# MAGIC     orphan_count,
# MAGIC     'Expected: orphan_count = 0' AS expected_result
# MAGIC FROM reference_checks
# MAGIC ORDER BY
# MAGIC     CASE WHEN orphan_count = 0 THEN 1 ELSE 0 END,
# MAGIC     orphan_count DESC,
# MAGIC     check_name;

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # **3.1 Reference integrity detail rows.**
# 
# Run/read this only when section 3 shows orphan_count > 0.

# CELL ********************

# MAGIC %%sql
# MAGIC WITH reference_details AS (
# MAGIC     SELECT
# MAGIC         'vehicle.customer_id -> customers.customer_id' AS check_name,
# MAGIC         CAST(v.vehicle_id AS STRING) AS child_pk,
# MAGIC         CAST(v.customer_id AS STRING) AS missing_parent_key
# MAGIC     FROM silver.vehicle v
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON v.customer_id = c.customer_id
# MAGIC     WHERE v.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(v.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.customer_id -> customers.customer_id',
# MAGIC         CAST(q.quotation_id AS STRING),
# MAGIC         CAST(q.customer_id AS STRING)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON q.customer_id = c.customer_id
# MAGIC     WHERE q.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(q.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.agent_id -> agents.agent_id',
# MAGIC         CAST(q.quotation_id AS STRING),
# MAGIC         CAST(q.agent_id AS STRING)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.agents a
# MAGIC         ON q.agent_id = a.agent_id
# MAGIC     WHERE q.agent_id IS NOT NULL
# MAGIC       AND TRIM(CAST(q.agent_id AS STRING)) <> ''
# MAGIC       AND a.agent_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation.provider_code -> insurance_providers.provider_code',
# MAGIC         CAST(q.quotation_id AS STRING),
# MAGIC         CAST(q.provider_code AS STRING)
# MAGIC     FROM silver.quotation q
# MAGIC     LEFT JOIN silver.insurance_providers p
# MAGIC         ON q.provider_code = p.provider_code
# MAGIC     WHERE q.provider_code IS NOT NULL
# MAGIC       AND TRIM(CAST(q.provider_code AS STRING)) <> ''
# MAGIC       AND p.provider_code IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'quotation_item.quotation_id -> quotation.quotation_id',
# MAGIC         CAST(qi.quotation_item_id AS STRING),
# MAGIC         CAST(qi.quotation_id AS STRING)
# MAGIC     FROM silver.quotation_item qi
# MAGIC     LEFT JOIN silver.quotation q
# MAGIC         ON qi.quotation_id = q.quotation_id
# MAGIC     WHERE qi.quotation_id IS NOT NULL
# MAGIC       AND TRIM(CAST(qi.quotation_id AS STRING)) <> ''
# MAGIC       AND q.quotation_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.quotation_id -> quotation.quotation_id',
# MAGIC         CAST(p.policy_id AS STRING),
# MAGIC         CAST(p.quotation_id AS STRING)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.quotation q
# MAGIC         ON p.quotation_id = q.quotation_id
# MAGIC     WHERE p.quotation_id IS NOT NULL
# MAGIC       AND TRIM(CAST(p.quotation_id AS STRING)) <> ''
# MAGIC       AND q.quotation_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.customer_id -> customers.customer_id',
# MAGIC         CAST(p.policy_id AS STRING),
# MAGIC         CAST(p.customer_id AS STRING)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.customers c
# MAGIC         ON p.customer_id = c.customer_id
# MAGIC     WHERE p.customer_id IS NOT NULL
# MAGIC       AND TRIM(CAST(p.customer_id AS STRING)) <> ''
# MAGIC       AND c.customer_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'policy.provider_code -> insurance_providers.provider_code',
# MAGIC         CAST(p.policy_id AS STRING),
# MAGIC         CAST(p.provider_code AS STRING)
# MAGIC     FROM silver.policy p
# MAGIC     LEFT JOIN silver.insurance_providers ip
# MAGIC         ON p.provider_code = ip.provider_code
# MAGIC     WHERE p.provider_code IS NOT NULL
# MAGIC       AND TRIM(CAST(p.provider_code AS STRING)) <> ''
# MAGIC       AND ip.provider_code IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'payment.policy_id -> policy.policy_id',
# MAGIC         CAST(pay.payment_id AS STRING),
# MAGIC         CAST(pay.policy_id AS STRING)
# MAGIC     FROM silver.payment pay
# MAGIC     LEFT JOIN silver.policy pol
# MAGIC         ON pay.policy_id = pol.policy_id
# MAGIC     WHERE pay.policy_id IS NOT NULL
# MAGIC       AND TRIM(CAST(pay.policy_id AS STRING)) <> ''
# MAGIC       AND pol.policy_id IS NULL
# MAGIC 
# MAGIC     UNION ALL
# MAGIC     SELECT
# MAGIC         'cancellation.policy_id -> policy.policy_id',
# MAGIC         CAST(can.cancellation_id AS STRING),
# MAGIC         CAST(can.policy_id AS STRING)
# MAGIC     FROM silver.cancellation can
# MAGIC     LEFT JOIN silver.policy pol
# MAGIC         ON can.policy_id = pol.policy_id
# MAGIC     WHERE can.policy_id IS NOT NULL
# MAGIC       AND TRIM(CAST(can.policy_id AS STRING)) <> ''
# MAGIC       AND pol.policy_id IS NULL
# MAGIC )
# MAGIC SELECT
# MAGIC     'REFERENCE_ORPHAN_DETAIL' AS check_type,
# MAGIC     check_name,
# MAGIC     child_pk,
# MAGIC     missing_parent_key
# MAGIC FROM reference_details
# MAGIC ORDER BY check_name, child_pk

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
