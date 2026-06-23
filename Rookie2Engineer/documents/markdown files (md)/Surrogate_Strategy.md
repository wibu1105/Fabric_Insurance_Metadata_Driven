# Surrogate Key Strategy

## Decision Rationale
We are adopting **GUID as the default surrogate key** for all tables unless explicitly specified otherwise. This ensures global uniqueness across multiple sources and prepares the system for future scalability.

- **GUID**  
  - Default choice for all tables.  
  - Best fit for **multi-source systems**.  
  - Guarantees uniqueness across environments.  
  - Future-proof if more sources are added.  

- **Autoincrement**  
  - Used only for tables explicitly tied to a **single-source system** (SQL-only).  
  - Lightweight and efficient for joins.  
  - Smaller storage footprint.

---

## Current Policy
- **Default:** All tables use **GUID** surrogate keys.  
- **Exceptions:** The following tables use **autoincrement** surrogate keys:  
  - DimCustomer  
  - DimAgent  
  - DimProvider  
  - DimVehicle  
  - DimQuotationInfo  
  - DimCoverageType  
  - FactQuotationItem  

- **Special Cases:** Policy, Cancel, and Payment tables use **GUID**, but their **fact tables** do not require GUID.  

---

## Trade-offs

| Key Type | Advantages | Disadvantages |
|----------|------------|---------------|
| **GUID** | - Globally unique across multiple sources<br>- Default choice for scalability<br>- No risk of collisions | - Larger size (36 characters)<br>- Slower joins and indexing<br>- Higher storage overhead |
| **Autoincrement** | - Lightweight and fast for joins<br>- Easy to implement<br>- Smaller storage footprint | - Only works reliably with single-source systems<br>- Risk of collisions if data comes from multiple sources |

---

## Implementation in PySpark

### Using GUID (Default)
staging_df is defined in the previous code.
```python
from pyspark.sql import functions as F

# Add a GUID surrogate key to your dimension dataframe
dim_customer_df = staging_df.withColumn("CustomerSK", F.expr("uuid()"))
```

> Note: Spark’s `uuid()` generates standard 36-character GUID strings.

---

### Using Autoincrement (Exceptions)
df is defined in the previous code.
```python
from pyspark.sql.functions import monotonically_increasing_id

# Generate IDs
df_dim = df.withColumn("CustomerKey", monotonically_increasing_id())
```

---