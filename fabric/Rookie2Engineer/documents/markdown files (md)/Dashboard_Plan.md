# Pipeline Monitoring Dashboard Plan

## 1. Overview
This document outlines the plan for the Pipeline Monitoring Dashboard, which provides visibility into the execution, performance, and data quality of the ETL pipelines. The dashboard relies on the `audit` and `cfg` schemas stored in the Lakehouse to generate actionable insights for Data Engineers and stakeholders.

---

## 2. Recommended Metrics

Based on the existing metadata architecture, the following metrics are recommended. They are chosen for their realistic application in monitoring pipeline health, debugging failures, and ensuring data quality.

### 2.1. Operational & Health Metrics
* **Pipeline Status**
  * **Source**: `audit_batch_log` & `audit_session_log` (`batch_status`, `session_status`)
  * **Use Case**: Provides a quick, real-time glance at overall system health. Allows operators to immediately know if the latest master batch or individual pipelines are Running, Succeeded, or Failed.
* **Success Rate (%)**
  * **Source**: `audit_session_log` (count of Succeeded vs. total sessions)
  * **Use Case**: Key Performance Indicator (KPI) for Service Level Agreements (SLAs). Helps leadership and engineering track the long-term stability of the pipelines.
* **Failed Run Number**
  * **Source**: `audit_session_log` & `audit_table_session_log` (count where status = 'Failed')
  * **Use Case**: Immediate alert indicator. A sudden spike in failed runs warrants immediate intervention by the on-call data engineer.
* **Matrix of Recent Runs**
  * **Source**: `audit_session_log` (`pipeline_name`, `session_start`, `session_end`, `session_status`)
  * **Use Case**: A visual heatmap or grid showing pipeline execution over time. Helps in identifying long-running pipelines and spotting temporal patterns in failures (e.g., pipelines always failing at midnight).

### 2.2. Performance & Volume Metrics
* **Data Volume Processed Trend**
  * **Source**: `audit_table_session_log` (`processed_rows`, `start_time`)
  * **Use Case**: Monitors the volume of data moving through the layers. A sudden, unexpected drop in processed rows could indicate an upstream source issue, even if the pipeline technically succeeds.
* **Pipeline Duration (Execution Time)**
  * **Source**: `audit_session_log` (`session_end` - `session_start`)
  * **Use Case**: Identifies performance bottlenecks. If a pipeline's duration gradually increases over time, it may require query optimization or a shift from a full load to an incremental load strategy.

### 2.3. Data Quality & Error Tracking
* **Top Errors by Code/Step**
  * **Source**: `audit_error_log` (`error_code`, `step_name`)
  * **Use Case**: Helps prioritize bug fixes. By grouping errors, engineers can identify the most frequent points of failure (e.g., source connection timeouts, schema mismatches) and fix the root causes.
* **Data Quality Degradation (Invalid Records)**
  * **Source**: `audit_invalid_record` (`invalid_record_count`, `invalid_reason`, `table_name`)
  * **Use Case**: Monitors the Silver layer's data cleansing process. High volumes of invalid records alert engineers to potential changes in source data formats or overly strict validation rules.

---

## 3. Dashboard Structure Plan

To prevent the dashboard from becoming cluttered, it is recommended to split it into three distinct pages (tabs), each serving a specific user persona and troubleshooting depth.

### Page 1: Executive Overview (High-Level Health)
**Target Audience**: Data Engineering Leads, Project Managers, Stakeholders
* **KPI Cards**: Latest Batch Status, Overall Success Rate (Last 7 Days), Total Failed Runs (Last 24h), Total Rows Processed.
* **Overall System Status**: A timeline or Gantt chart of the `00_Master_ETL` batch execution.
* **Processed Volume Trend**: A line chart showing `processed_rows` over time.

### Page 2: Pipeline & Session Execution (Operational View)
**Target Audience**: Data Engineers, Operations Team
* **Matrix of Recent Runs**: A heatmap showing pipelines on the Y-axis, dates on the X-axis, color-coded by status (Green=Success, Red=Failed, Yellow=Running).
* **Pipeline Duration Analysis**: Bar charts comparing the average duration of pipelines to identify bottlenecks.
* **Layer Load Distribution**: Donut chart showing the breakdown of load types (Full vs. Incremental) currently active, sourced from `cfg_landing_bronze_table` and `cfg_silver_gold_table`.

### Page 3: Data Quality & Error Monitoring (Troubleshooting View)
**Target Audience**: Data Engineers, Data Quality Analysts
* **Error Frequency Bar Chart**: Top 5 error codes and the steps they occurred in.
* **Invalid Records Breakdown**: A Tree Map or Bar Chart showing the count of invalid records categorized by `invalid_reason` and `table_name`.
* **Detailed Logs Table**: A drill-down table combining `audit_error_log` and `audit_invalid_record` to allow engineers to see the exact `record_payload` or `error_name` for debugging purposes. Filters should be available for Session ID and Date.

---

## 4. Power BI DAX Calculations

The following tables provide the recommended DAX (Data Analysis Expressions) formulas to calculate all KPIs and measures matching the Dashboard's UI layout. **All measures below have the dynamic "Last N Days" filter logic baked in directly via CALCULATE.**

### 4.1. ETL Overview Page

| Metric | DAX Formula | Description |
| :--- | :--- | :--- |
| **Latest Batch Status** | `Latest Batch Status = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) VAR MaxDateInPeriod = CALCULATE(MAX('audit_batch_log'[session_start]), FILTER('audit_batch_log', 'audit_batch_log'[session_start] >= CutoffDate)) RETURN CALCULATE(MAX('audit_batch_log'[batch_status]), FILTER('audit_batch_log', 'audit_batch_log'[session_start] = MaxDateInPeriod))` | Retrieves the status of the most recent pipeline batch execution within the selected period. |
| **Total Batches** | `Total Batches = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_batch_log'), FILTER('audit_batch_log', 'audit_batch_log'[session_start] >= CutoffDate))` | Counts the total number of master pipeline batches in the period. |
| **Success Batches** | `Success Batches = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_batch_log'), FILTER('audit_batch_log', 'audit_batch_log'[batch_status] = "success" && 'audit_batch_log'[session_start] >= CutoffDate))` | Counts the number of master batches that successfully completed in the period. |
| **Total Sessions** | `Total Sessions = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_session_log'), FILTER('audit_session_log', 'audit_session_log'[session_start] >= CutoffDate))` | Counts the total number of pipeline execution sessions in the period. |
| **Success Sessions** | `Success Sessions = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_session_log'), FILTER('audit_session_log', 'audit_session_log'[session_status] = "success" && 'audit_session_log'[session_start] >= CutoffDate))` | Counts the number of pipeline execution sessions that successfully completed in the period. |
| **Success Rate** | `Success Rate = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN DIVIDE(CALCULATE(COUNTROWS('audit_session_log'), FILTER('audit_session_log', 'audit_session_log'[session_status] = "success" && 'audit_session_log'[session_start] >= CutoffDate)), CALCULATE(COUNTROWS('audit_session_log'), FILTER('audit_session_log', 'audit_session_log'[session_start] >= CutoffDate)), 0)` | Calculates the percentage of successful runs in the period. |
| **Failed Sessions** | `Failed Sessions = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_session_log'), FILTER('audit_session_log', 'audit_session_log'[session_status] = "failed" && 'audit_session_log'[session_start] >= CutoffDate))` | Counts the number of sessions that failed in the period. |
| **Avg Batch Duration (mins)** | `Avg Batch Duration = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(AVERAGEX('audit_batch_log', DATEDIFF([session_start], [session_end], MINUTE)), FILTER('audit_batch_log', 'audit_batch_log'[session_start] >= CutoffDate && 'audit_batch_log'[batch_status] = "success"))` | Calculates the average execution time in minutes for successful master batches in the period. |
| **Session Duration (Mins)** | `Session Duration = VAR StartTime = MIN('audit_session_log'[session_start]) VAR EndTime = MAX('audit_session_log'[session_end]) RETURN IF(ISBLANK(EndTime), DATEDIFF(StartTime, NOW(), MINUTE), DATEDIFF(StartTime, EndTime, MINUTE))` | Evaluates the duration of individual sessions. For sessions still running (no end time), it calculates the elapsed time up to now. |

### 4.2. Table Load Monitoring Page

| Metric | DAX Formula | Description |
| :--- | :--- | :--- |
| **Total Tables Processed** | `Total Tables Processed = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_table_session_log'), FILTER('audit_table_session_log', 'audit_table_session_log'[start_time] >= CutoffDate))` | Total count of table loads processed in the period. |
| **Succeeded Tables** | `Succeeded Tables = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_table_session_log'), FILTER('audit_table_session_log', 'audit_table_session_log'[status] = "success" && 'audit_table_session_log'[start_time] >= CutoffDate))` | Count of tables that were successfully loaded in the period. |
| **Failed Tables** | `Failed Tables = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_table_session_log'), FILTER('audit_table_session_log', 'audit_table_session_log'[status] = "failed" && 'audit_table_session_log'[start_time] >= CutoffDate))` | Count of tables that failed during loading in the period. |
| **Total Processed Rows** | `Total Processed Rows = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(SUM('audit_table_session_log'[processed_rows]), FILTER('audit_table_session_log', 'audit_table_session_log'[start_time] >= CutoffDate))` | Sums up all processed rows across all table loads in the period. |
| **Avg Table Duration (mins)** | `Avg Table Duration = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(AVERAGEX('audit_table_session_log', DATEDIFF('audit_table_session_log'[start_time], 'audit_table_session_log'[end_time], MINUTE)), FILTER('audit_table_session_log', 'audit_table_session_log'[start_time] >= CutoffDate && 'audit_table_session_log'[status] = "success"))` | Calculates the average execution time per successfully loaded table in the period. |

### 4.3. Error & Data Quality Page

| Metric | DAX Formula | Description |
| :--- | :--- | :--- |
| **Total Errors** | `Total Errors = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_error_log'), FILTER('audit_error_log', 'audit_error_log'[error_time] >= CutoffDate))` | Counts the total number of logged system or pipeline errors in the period. |
| **Failed Table Sessions** | `Failed Table Sessions = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(COUNTROWS('audit_table_session_log'), FILTER('audit_table_session_log', 'audit_table_session_log'[status] = "failed" && 'audit_table_session_log'[start_time] >= CutoffDate))` | Same logic as Failed Tables, counting the failed runs in the period. |
| **Invalid Record Count** | `Invalid Record Count = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(SUM('audit_invalid_record'[invalid_record_count]), FILTER('audit_invalid_record', 'audit_invalid_record'[rejected_timestamp] >= CutoffDate))` | Sums the total count of records failing data quality validation in the period. |
| **Tables With Invalid Data** | `Tables With Invalid Data = VAR CutoffDate = TODAY() - SELECTEDVALUE(DateParameter[Days], 7) RETURN CALCULATE(DISTINCTCOUNT('audit_invalid_record'[table_name]), FILTER('audit_invalid_record', 'audit_invalid_record'[rejected_timestamp] >= CutoffDate))` | Counts the unique number of tables that reported invalid data records in the period. |

---

## 5. Visualizations & Data Mapping

This section defines how each visual in the dashboard uses the underlying Lakehouse tables and columns. Because `gold.dimdate` is not physically connected to the audit schemas, any visualizations that plot data over time must use the native timestamp columns from the audit tables (e.g., `session_start`, `start_time`, `error_time`) for their axes. The `DateParameter` slicer handles filtering dynamically via the measures. Ensure the rest of your Power BI data model has relationships built properly: `audit_session_log` acts as a parent to `audit_table_session_log`, which in turn acts as a parent to `audit_error_log` and `audit_invalid_record` via `audit_table_session_id`.

### 5.1. ETL Overview Page
* **Batch Duration by Date (mins)**
  * **Visual Type**: Area Chart or Line Chart.
  * **X-Axis**: `audit_batch_log`[`session_start`] (Formatted to show just the Date).
  * **Y-Axis**: `Avg Batch Duration` (Measure).
  * **Relationships**: No date table relationship is required; this plots the native timestamp directly.
* **Session Status Distribution**
  * **Visual Type**: Stacked Bar Chart.
  * **Category (Y-Axis)**: `audit_session_log`[`session_status`].
  * **Value (X-Axis)**: `Total Sessions` (Measure).
* **Latest Batch Details**
  * **Visual Type**: Table.
  * **Columns**: `audit_session_log`[`audit_batch_id`], `audit_session_log`[`pipeline_name`], `audit_session_log`[`session_status`], `audit_session_log`[`session_start`], `audit_session_log`[`session_end`], `Duration (Mins)` (Measure).

### 5.2. Table Load Monitoring Page
* **Table Status by Layer**
  * **Visual Type**: 100% Stacked Column Chart.
  * **X-Axis**: `audit_table_session_log`[`layer_name`] (or `DimLayer`[`layer_name`] for custom sorting).
  * **Legend**: `audit_table_session_log`[`status`].
  * **Value**: Count of `audit_table_session_log`[`audit_table_session_id`].
* **Data Volume by Layer (Processed Rows)**
  * **Visual Type**: Funnel Chart (Highly Recommended) or Donut Chart.
  * **Category**: `audit_table_session_log`[`layer_name`] (or `DimLayer`[`layer_name`]).
  * **Values**: `Total Processed Rows` (Measure).
  * **Use Case**: Visually displays the volume of data moving through the pipeline. A Funnel chart perfectly illustrates how raw data is reduced/aggregated as it moves from Landing -> Bronze -> Silver -> Gold.
* **Slowest Tables (Duration in mins)**
  * **Visual Type**: Clustered Column Chart.
  * **X-Axis**: `cfg_landing_bronze_table`[`destination_table`] OR `cfg_silver_gold_table`[`target_table`]. Note: Because `audit_table_session_log` only contains `table_id`, you must join it to the `cfg` tables on `table_id` to retrieve the human-readable table name.
  * **Y-Axis**: `Avg Table Duration (mins)` (Measure).

### 5.3. Error & Data Quality Page
* **Errors by ETL Step**
  * **Visual Type**: Column Chart.
  * **X-Axis**: `audit_error_log`[`step_name`].
  * **Y-Axis**: `Total Errors` (Measure).
* **Invalid Records by Reason**
  * **Visual Type**: Donut Chart
  * **Legend**: `audit_invalid_record`[`invalid_reason`].
  * **Values**: `Invalid Record Count` (Measure).

---

## 6. Implementing the "Last N Days" Slicer

To create a dynamic "Last 7 Days", "Last 14 Days", etc., dropdown slicer in Power BI, you must use a **Disconnected Table** combined with the DAX measures provided above.

### Step 1: Create a Disconnected Parameter Table
In Power BI, you can create this table using a DAX calculated table. Go to the **Modeling** tab, click **New Table**, and enter the following DAX calculation:

```dax
DateParameter = 
DATATABLE (
    "Period", STRING,
    "Days", INTEGER,
    "Order", INTEGER,
    {
        {"Last 7 Days", 7, 1},
        {"Last 14 Days", 14, 2},
        {"Last 30 Days", 30, 3},
        {"All Time", 9999, 4}
    }
)
```

*Do NOT create a relationship between this table and your data model.* Select the `Period` column in the Data view, go to **Column tools**, and click **Sort by column** -> `Order` so it appears logically in the slicer.

### Step 2: Create a Slicer
Add a Slicer visual to your dashboard and drop the `DateParameter[Period]` column into it. 

Because the `CALCULATE` logic is now baked directly into the measures in Section 4, the visuals will automatically filter based on the slicer selection without needing any extra visual-level filters!

---

## 7. UI Enhancements & Semantic Model Fixes

The following configurations should be applied to enhance the dashboard's user experience and handle Fabric Direct Lake limitations.

### 7.1. Clean Date Formatting on X-Axis
When plotting continuous datetime columns (e.g., `session_start`), Power BI may display the exact time on the axis (like 12AM, 12PM). To force clean dates:
1. In the Fabric Semantic Model web interface, select the `session_start` column.
2. In the Properties pane, change **Format** to a Short Date string (e.g., `dd-MMM-yyyy`).
3. In Power BI Desktop, click on the Line Chart visual, go to the **Format your visual** pane -> **X-axis**.
4. Change the **Type** from **Continuous** to **Categorical**. This groups the data perfectly by date.

### 7.2. Custom Sorting for Layers and Statuses
To force charts to display categories in a logical sequence instead of alphabetical order, use small Dimension Tables with an `Order` column. In the Semantic Model properties, set the text column to **Sort by column** -> `Order`.

**DimLayer Table (landing -> bronze -> silver -> gold):**
```dax
DimLayer = 
DATATABLE (
    "layer_name", STRING,
    "Order", INTEGER,
    {
        {"landing", 1},
        {"bronze", 2},
        {"silver", 3},
        {"gold", 4}
    }
)
```
*Tip: On your Layer chart, right-click `layer_name` in the X-axis well and select "Show items with no data" so all layers are always visible, even if the count is 0.*

**DimStatus Table (Started -> Running -> success -> Failed):**
```dax
DimStatus = 
DATATABLE (
    "Status", STRING,
    "Order", INTEGER,
    {
        {"Started", 1},
        {"Running", 2},
        {"success", 3},
        {"Failed", 4}
    }
)
``