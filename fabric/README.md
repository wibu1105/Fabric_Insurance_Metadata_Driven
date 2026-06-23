# Rookie2Engineer - Data Engineering Project

## Project Overview
Rookie2Engineer is an end-to-end data engineering pipeline designed for an insurance business. The project ingests, transforms, and serves insurance data—including quotations, policies, payments, and cancellations—to enable downstream analytics and Business Intelligence (BI) reporting. 

Built on **Microsoft Fabric**, the solution implements a modern **Medallion Architecture** (Landing, Bronze, Silver, Gold) and utilizes a metadata-driven approach to seamlessly manage both full and incremental data loads.

## Architecture & Data Flow
The pipeline follows a structured data flow to ensure data quality, traceability, and performance:

1. **Source Systems (Raw Data)**
   - **Insurance CRM (SQL Server):** Customer and quotation transactional data.
   - **Incremental Files (JSON):** Insurance policy, payment, and cancellation records.

2. **Landing Layer**
   - Initial storage zone for raw ingested data.
   - Supports both `Append` (Incremental) and `Full Load` strategies based on metadata configuration.

3. **Bronze Layer**
   - Stores raw historical data with minimal transformation.
   - Maintains raw history and supports Change Data Capture (CDC) patterns using watermark columns.

4. **Silver Layer**
   - **Transformations:** Data cleansing (null handling, deduplication), standardization (type casting), and integration.
   - **Output:** Business-ready, normalized data stored in the Silver Lakehouse schema.

5. **Gold Layer**
   - **Dimensional Modeling:** Builds Star Schemas (Fact and Dimension tables) optimized for analytics.
   - **SCD Processing:** Applies Slowly Changing Dimensions (SCD) for dimensions and append logic for facts.

6. **Business Intelligence Layer**
   - Final curated data consumed by **Power BI** for operational reporting and dashboard visualizations.

## Repository Structure
- **`Carpro/`**: Requirements and mock data
- **`Rookie2Engineer/fabric_source/`**: Contains Microsoft Fabric artifacts including Lakehouses (`Rookie2Engineer_Lakehouse.Lakehouse`), SQL databases, metadata folders, and transformation pipelines for each Medallion layer (e.g., `raw_to_landing_folder`, `bronze_to_silver_folder`).
- **`Rookie2Engineer/documents/`**: Extensive Markdown documentation covering architecture, data flows, business processes (Quotation Lifecycle, Policy Issuance), and table structures.

## Business Process Context
Understanding the domain is critical for data modeling. The pipeline supports two core lifecycles:
- **Insurance Quotation Lifecycle:** Tracks submissions, risk assessment, pricing, negotiation, and the final binding/rejection decision.
- **Policy Issuance Process:** Manages the active policy contract, including verification, premium confirmation, payment collection, claims handling, and renewals or cancellations.

For deeper insights, please refer to the detailed documentation located in `Rookie2Engineer/documents/markdown files (md)/`.