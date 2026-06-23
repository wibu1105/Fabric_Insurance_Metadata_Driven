# Define End-to-end Dataflow Documentation

![Dataflow](/Rookie2Engineer/documents/images/dataflow.png)
<p align="center">
  <em>End-to-end Dataflow</em>
</p>

## Overview
This document describes the end-to-end data flow architecture from raw source systems to reporting and analytics consumption.  
The solution follows a modern Medallion Architecture approach with the following layers:

- Landing Layer
- Bronze Layer
- Silver Layer
- Gold Layer
- Business Intelligence Layer

---

# 1. Source Systems (Raw Data)

The system ingests data from multiple raw data sources:

| Source System | Source Type | Description |
|---|---|---|
| Customer & Quotation (CRM) | SQL Server | Stores customer and quotation transactional data |
| Policy & Payment | JSON Files | Stores insurance policy and payment information |

---

# 2. Landing Layer

## Purpose
The Landing Layer acts as the initial storage zone for raw ingested data before transformation.

## Processing Logic

### Metadata-Driven Load Control
Before ingestion begins, the pipeline checks a metadata configuration table to determine the load strategy:

- Incremental Load
- Full Load

---

## Incremental Load Flow

### Process
- Load data using watermark column
- Append new records into Landing Layer

### Characteristics
- Optimized for daily/incremental ingestion
- Reduces processing time
- Prevents reloading historical data

### Load Type
`Append`

---

## Full Load Flow

### Process
- Load all source data
- Add ETL execution date column
- Append data into Landing Layer

### Characteristics
- Reloads complete dataset from source
- Preserves historical snapshots by ETL date
- Used for initial loads or recovery scenarios

### Load Type
`Append`

---

# 3. Bronze Layer

## Purpose
The Bronze Layer stores raw historical data with minimal transformation.

## Processing Logic

A second metadata configuration check determines the Bronze loading strategy:

- Incremental Load
- Full Load

---

## Incremental Bronze Load

### Process
- Load data using watermark column
- Overwrite latest snapshot if required

### Characteristics
- Maintains raw history
- Supports CDC-like ingestion pattern

---

## Full Bronze Load

### Process
- Perform full load using max ETL date logic
- Overwrite Bronze tables

### Characteristics
- Rebuilds Bronze tables completely
- Ensures source consistency

---

# 4. Silver Layer

## Purpose
The Silver Layer performs data cleansing, standardization, and integration.

## Main Transformations

| Transformation Type | Description |
|---|---|
| Data Cleansing | Remove invalid or duplicate records |
| Standardization | Standardize data types and formats |
| Integration | Combine related datasets |

---

## Processing Characteristics

- Business-ready cleaned data
- Consistent schema structure
- Improved data quality
- Intermediate analytical layer

---

## Silver Layer Output

### Storage
- Silver Schema in Lakehouse

### Data Quality Activities
- Null handling
- Data type casting
- Deduplication
- Validation checks
- Data normalization

---

# 5. Gold Layer

## Purpose
The Gold Layer provides business-oriented dimensional models optimized for analytics and reporting.

---

## Main Processing Activities

### Dimensional Modeling
- Build Star Schema models
- Create Fact and Dimension tables

### Aggregation
- Generate aggregated business metrics
- Improve reporting performance

### SCD Processing
- Apply SCD Merge for Dimensions
- Append loading for Fact tables

---

## Gold Layer Output

### Storage
- Gold Schema in Lakehouse

### Key Deliverables
| Object Type | Description |
|---|---|
| Dimension Tables | Business descriptive entities |
| Fact Tables | Business transactional measurements |
| Aggregated Tables | Pre-calculated analytical metrics |

---

# 6. Business Intelligence Layer

## Purpose
The final curated Gold data is consumed for reporting and analytics.

## Consumption Tools

| Tool | Purpose |
|---|---|
| Power BI | Dashboard and visualization |
| Reports | Business operational reporting |

---

# End-to-End Data Flow Summary

```text
Raw Sources
    ↓
Landing Layer
    ↓
Bronze Layer
    ↓
Silver Layer
    ↓
Gold Layer
    ↓
Power BI / Reports
```
